# Design sketch: threaded decoupled renderer + input (web port)

Status: **implementation sketch** — no work started. Companion to
`emscripten-asyncify-removal.md` (which decides *whether*; this details *how*
for the threads path). Assumes cross-origin isolation is acceptable (COOP
`same-origin` + COEP `require-corp`; CDN sends `Cross-Origin-Resource-Policy:
cross-origin`; cloud OAuth moved to a redirect flow).

## Try PROXY_TO_PTHREAD first (low-effort; removes ASYNCIFY without decoupling)

Before the hand-rolled split below, spike emscripten's built-in
`-sPROXY_TO_PTHREAD`: it runs `main()` and the whole blocking engine loop on a
spawned pthread, with the browser main thread as the proxy/UI thread.
Emscripten auto-proxies the main-thread-only calls (GL, DOM, SDL events,
audio) back to the UI thread — or with `-sOFFSCREENCANVAS_SUPPORT` the GL runs
directly on the worker (no per-call proxying).

- The worker's `SDL_Delay` becomes a **real blocking sleep** → **drop
  `-sASYNCIFY` entirely.** That's the whole win, essentially for a build-flag
  change (`-pthread -sPROXY_TO_PTHREAD [-sOFFSCREENCANVAS_SUPPORT]`), near-zero
  ScummVM code.
- **Dynamic linking works with pthreads:** emscripten 6.0.2 propagates
  already-loaded side modules to each spawned thread (`sharedModules` in
  `runtime_pthread.js`), so MAIN_MODULE + 125 SIDE_MODULE plugins are not a
  blocker (verify: plugins are loaded before the engine thread starts).
- **Fixes the `silence_callback` crash for free** — that bug was ASYNCIFY
  re-entry corruption; with ASYNCIFY gone there is no asyncify state to corrupt.

What PROXY_TO_PTHREAD does **not** give you:
- It removes ASYNCIFY but does **not** decouple the render.
  `updateScreen → SDL_GL_SwapWindow` still fires at the *engine's* cadence
  (just on/proxied-from the worker), not a main-thread rAF — so no
  cursor-tracks-pointer latency win and no automatic black-bar coordinate fix.
  Those need the shared-surface producer/consumer below.
- It keeps you on SDL3's emscripten threaded GL/event/audio paths, whose
  maturity is uncertain (the port is still flagged experimental).

**So the layering is:** (1) spike PROXY_TO_PTHREAD to remove ASYNCIFY cheaply;
(2) build the hand-rolled decoupled split below only if GL proxying is too slow
*and* OffscreenCanvas isn't enough, or SDL3-pthreads proves too immature, or
you specifically want the render-decoupling wins. The split can also sit *on
top of* PROXY_TO_PTHREAD (engine on the proxied pthread; a custom main-thread
rAF presenter reads the shared surface).

## The cut line (why the hand-rolled decoupling is clean in ScummVM)

Two facts from the source make a producer/consumer split natural:

- The GL backend keeps the frame as **RAM surfaces** — `_gameScreen`,
  `_overlay`, `_cursor` (+ mask/palette/hotspot) are `OpenGL::Surface`s that
  wrap CPU pixels; `updateScreen()` uploads dirty ones to GL textures, then
  composites + `SDL_GL_SwapWindow`. The GL texture is a *cache*, not the source
  of truth.
- Engines only ever touch the backend through `OSystem` (`copyRectToScreen`,
  `updateScreen`, `setMouseCursor`, `pollEvent`, `delayMillis`, `getMillis`).

So we split along that line, with **zero engine changes** (a new backend, like
the http/curl vs http/emscripten split — other platforms untouched):

- **Engine worker (pthread):** runs `main()` and the blocking engine loop.
  Owns all RAM surfaces, engine logic, the mixer, timers. `delayMillis` does a
  *real* timed block (futex) — no `emscripten_sleep`, no ASYNCIFY.
- **Presenter (browser main thread):** owns the WebGL context + canvas + DOM.
  A `requestAnimationFrame` loop reads the published surfaces from shared
  memory, uploads dirty regions to GL textures, composites (game + overlay +
  cursor, with scaling/aspect), presents. DOM listeners capture input, map
  coordinates, and push events into a shared ring.

The engine stays single-threaded (one worker); the *only* concurrency is the
backend↔presenter boundary, mediated by lock-free structures.

## Shared-memory boundary

One `SharedArrayBuffer` (the wasm shared Memory) carrying three channels:

1. **Surface channel** (worker → presenter), double/triple-buffered:
   - Pixel buffers for `_gameScreen`, `_overlay`, `_cursor` (+ mask), allocated
     *in shared memory*.
   - Per-surface metadata: dims, GL-ready format, dirty rect(s), a
     `mode-generation` counter.
   - Publication = flip the front/back index + bump an atomic `frameSeq`. The
     worker writes back buffer B while the presenter reads front buffer A; no
     locks, no tearing.
2. **Input ring** (presenter → worker): lock-free SPSC ring of encoded
   `Common::Event`s (type, x, y, keycode, mods, timestamp). Single producer
   (main thread), single consumer (worker) → just atomic head/tail.
3. **Control/sync words** (atomics): `frameSeq`, the `delayMillis` futex,
   shared cursor position, `overlayVisible`, `mode-generation`, `quit`.

## Backend responsibilities (worker side)

New `OSystem_EmscriptenThreaded` + `ThreadedGraphicsManager`:

- `copyRectToScreen` / `lockScreen`: write into the shared `_gameScreen` buffer
  (unchanged contract; the buffer just lives in shared memory).
- **Format conversion on the worker.** CLUT8 games carry a palette; convert to
  the GL-ready RGBA into the shared buffer before publishing, so the boundary
  is format-agnostic and the presenter just uploads. (ScummVM already does this
  conversion in the upload path — move that CPU step to the worker.)
- `updateScreen`: mark dirty rects, flip the double-buffer index, bump
  `frameSeq`, optionally `Atomics.notify` the presenter. **No GL. No swap.**
- `setMouseCursor` / `showMouse`: publish cursor bitmap + hotspot + mask +
  palette + key color + visibility (only when the engine changes them).
- `warpMouse`: override the shared cursor-position word (see below).
- `initGraphics` / `setGraphicsMode`: allocate new shared surface buffers,
  bump `mode-generation`, publish new dims/format; the presenter reallocates
  its textures on the next rAF keyed off that generation.
- `delayMillis(n)`: **the ASYNCIFY-killer** — `emscripten_futex_wait`
  (or `pthread_cond_timedwait`) on the futex word with timeout `n`. Real
  thread sleep; the presenter can `Atomics.notify` to wake it early when input
  arrives (bounds input latency below the sleep). `checkTimers()` pumped after,
  as today — but now the sleep is honest.
- `getMillis`: the worker's own monotonic clock (`emscripten_get_now`); no
  cross-thread needed.
- `pollEvent`: `EmscriptenThreadedEventSource` drains the input ring → returns
  `Common::Event`s. No SDL event pump on the worker.

## Presenter responsibilities (main thread)

Pure JS + WebGL (or a thin main-thread wasm entry), driven by `rAF`:

- **Compose + present:** read front surfaces at `frameSeq`; upload dirty
  regions of game/overlay/cursor to GL textures; draw game quad → overlay (if
  `overlayVisible`) → cursor at the **live** pointer position; apply
  aspect/scaling/filtering (GPU); present. Re-upload whole small textures first
  (~1.4 MB game RGBA), optimize to dirty-rect uploads later.
- **Input capture:** DOM mouse/key/touch listeners → coordinate mapping (the
  game-rect transform lives here, since the presenter owns the display
  transform — this also fixes the black-bar cursor-clip cleanly) → encode →
  push to the input ring. Normally the presenter writes the shared
  cursor-position word from the DOM; `warpMouse` from the engine overrides it.
- **Mode changes:** on a new `mode-generation`, reallocate GL textures to the
  published dims before uploading (version each frame with the generation so a
  new-size surface never lands in an old-size texture).

## The wins that fall out of decoupling

- **No ASYNCIFY:** blocking loop runs natively on the worker; `delayMillis`
  genuinely sleeps. Removes the size blowup, speed penalty, `ASYNCIFY_IMPORTS`
  bookkeeping, and the re-entry bug class.
- **Cursor glued to the pointer:** the presenter composites the cursor at the
  *live* DOM position every rAF, even while the engine is mid-frame → no cursor
  lag on engine hitches. A real UX improvement over today.
- **Coordinate mapping lives with the display transform** → the black-bar
  input-clip issue disappears by construction.
- **SDL-thread-maturity is largely bypassed.** Because we hand-roll present +
  input across the boundary (rather than letting `PROXY_TO_PTHREAD`
  auto-proxy SDL's GL/event calls per-call), the immaturity of SDL3's
  emscripten thread/OffscreenCanvas support matters much less — an argument for
  this hand-rolled split over the naive proxy approach.
- **Audio race class removable (bonus):** with the mixer on the worker, feed an
  **AudioWorklet** on the main thread via a shared PCM ring. That eliminates
  the `silence_callback`/ASYNCIFY-audio re-entry crash (commit c663ad7ab10) at
  the root — the mixer writes PCM to a ring instead of dynCalling into
  possibly-suspended wasm. Out of scope for render+input, enabled by the same
  threading.

## Frictions / risks (ScummVM-specific)

- **Synchronous readback** (`grabScreen`, save thumbnails, some transitions):
  the worker holds the RAM surfaces, so readback is local + synchronous — fine.
- **`updateScreen` timing:** a few engines treat `updateScreen()` as "frame is
  on screen" for fade timing. With async present it returns before the frame
  shows; visually equivalent for time-polled fades. If any engine truly needs
  "present happened", expose a published `frameShownSeq` it can wait on (add
  only if a real case appears — do not build speculatively).
- **Build surface:** `-pthread` on the main module *and all 125 SIDE_MODULE
  plugins* → shared memory + dynamic linking + threads is emscripten's
  thorniest corner (called out in the decision doc). Biggest risk; prototype on
  a couple of plugins first.
- **iOS memory ceiling:** shared memory constrains `memory.grow` and iOS
  reserves against MAXIMUM_MEMORY; we're already at the 640 MB edge. Measure
  early on device.
- **COOP/COEP integration work:** CDN CORP header + OAuth redirect flow.

## Build mechanics

- `-pthread` main + plugins; shared Memory; COOP/COEP served.
- Topology: `main()` on a worker via `PROXY_TO_PTHREAD`. For the hand-rolled
  split the worker never calls GL — the browser main thread runs the presenter
  (creates the WebGL context, runs the rAF loop + DOM listeners, reads/writes
  the shared channels). For the plain PROXY_TO_PTHREAD spike, skip the presenter
  and let emscripten proxy GL/events (or `-sOFFSCREENCANVAS_SUPPORT` for GL on
  the worker) — that alone removes ASYNCIFY; layer the presenter on later for
  the decoupling wins.
- Keep everything funnelled through `OSystem` so the *engine* is identical to
  every other platform — this is a new backend, not an engine change.

## Component checklist

1. `OSystem_EmscriptenThreaded` + `ThreadedGraphicsManager` (worker).
2. `EmscriptenThreadedEventSource` (worker, drains input ring).
3. Presenter: WebGL compose/present + DOM input + coordinate mapping (main).
4. Shared-memory layout: double-buffered surface channel, SPSC input ring,
   atomics (frameSeq / futex / cursor-pos / mode-gen / quit).
5. Build: `-pthread` main + plugins, COOP/COEP, CDN CORP, OAuth redirect.
6. (Optional companion) AudioWorklet + shared PCM ring.

## Relationship to the other options

This is the *thread* realization of the decoupled-render idea. The **same
decoupling** (engine produces surfaces + reads an input queue; a separate
present/input stage) is also the shape a **JSPI** migration wants — there the
"separate stage" is the same single thread resumed via VM stack-switching
instead of a second thread. So building the decoupled backend is the
no-regret step regardless of which yield transport (ASYNCIFY today, JSPI later,
threads if JSPI stalls) ends up underneath.
