# Exploration: getting rid of ASYNCIFY on the web port

Status: **adversarial investigation only** — no work started. Written
2026-07-18. Companion to `multiplayer-web.md`.

Question: can we drop ASYNCIFY? We own the rendering, input, and timer
abstractions (`OSystem`) — could we use them to "hold" execution on the
browser's render-frame callback instead? Do we need threads? What are the
no-thread options? (Threads pull in COOP/COEP, which breaks our cross-origin
CDN and the OAuth/cloud flow — so they're expensive here specifically.)

## Why ASYNCIFY exists here (the constraint, verified in source)

- The build links the main module with `-s ASYNCIFY=1 -s
  ASYNCIFY_STACK_SIZE=1048576` (`configure:3391`); every plugin is
  `SIDE_MODULE=1 -s ASYNCIFY=1` with a narrowed import list (`configure:5246`,
  see task #39).
- **There is no `emscripten_set_main_loop` anywhere in the tree.** The port is
  pure blocking loops. `engines/engine.cpp` and each of the **125 engine
  directories** run their own deeply-nested
  `while (!quit) { pollEvent(); updateGame(); updateScreen(); delayMillis(n); }`
  — plus blocking waits inside cutscene players, script interpreters, dialog
  code, etc.
- The single yield point is `OSystem_Emscripten::delayMillis()` →
  `SDL_Delay()` → `emscripten_sleep()`. ASYNCIFY unwinds the entire C++ stack
  there, returns to the browser event loop, and rewinds on the next tick.
  Timers are pumped cooperatively right after (`checkTimers()`), because SDL
  timers don't fire under this model.
- The render present (`SDL_GL_SwapWindow`, `openglsdl-graphics.cpp:652`) and
  input polling happen *inside* that same blocking stack.

Cost of ASYNCIFY: binary-size blowup (binaryen instruments every function that
can sit on a suspendable stack), a per-call speed penalty, the 1 MB asyncify
stack, the `ASYNCIFY_IMPORTS` bookkeeping (task #39), and a recurring class of
re-entry bugs (the SDL3 `silence_callback` iOS crash `c663ad7ab10`, the
recorder timer stalls, the HTTP busy-wait interactions).

## The core obstacle to the "hold on the render frame" idea

Owning the `OSystem` abstraction lets us choose the **yield point** cleanly
(`delayMillis`/`updateScreen`/`pollEvent` are the natural boundary). It does
**not** let us avoid the hard part: to return control to the browser's
`requestAnimationFrame` from deep inside an engine's blocking loop, the native
C++ stack must be **unwound or parked**. You cannot block the browser main
thread and also let it paint.

So the real taxonomy is "how do we suspend a blocking native stack and resume
it later" — and there are exactly four answers. The abstraction we own decides
*where* we suspend; it can't remove the *need* to suspend.

## The four options

### A. Compiler-instrumented unwind — ASYNCIFY (current)
Binaryen rewrites functions into resumable state machines. Single-threaded, no
COOP/COEP, works everywhere including iOS Safari. Cost: size + speed +
re-entry hazards. We've already narrowed it (#39) to trim the cost.

### B. VM-native stack switching — JSPI (the ideal target)
`-sJSPI` (formerly `ASYNCIFY=2`) is a **drop-in replacement**: same
single-threaded model, **same yield points** (our `OSystem` abstraction), but
the browser VM performs the suspend/resume instead of compiler instrumentation.
Result: no code-size blowup, no per-call penalty, no `ASYNCIFY_IMPORTS` list,
and the re-entry bug class largely disappears (real native stacks, not a
hand-rolled state machine). Still no COOP/COEP requirement.
- **Blocker: Safari has not shipped it.** As of 2026 JSPI is W3C Phase 4
  (standardized) and ships in Chrome 137 + Firefox 139 (Firefox behind a
  flag); Safari only *removed its objection* in late 2025 and has an
  implementer assigned — not available. For an iOS-heavy audience (the whole
  reason we cap memory at 640 MB and chase Safari OOMs) that is disqualifying
  *today*, but it is the migration target, not a dead end.

### C. Real native stack on a worker — pthreads / PROXY_TO_PTHREAD
Run the whole ScummVM loop on a Web Worker that can **genuinely block** on
`delayMillis` (a real futex/`Atomics.wait`), while the UI thread pumps rAF,
input, and presents via OffscreenCanvas. No stack tricks at all — the blocking
loop simply blocks, on a thread that's allowed to.
- **Requires SharedArrayBuffer → cross-origin isolation** (`COOP: same-origin`
  + `COEP: require-corp`). That is precisely what breaks this deployment:
  - Every cross-origin asset (all game data on `scummvm-data.kuendig.io`) must
    then send `Cross-Origin-Resource-Policy`/CORS-for-CORP headers or it won't
    load. We already removed COEP earlier this project because it broke the CDN
    on Safari.
  - The OAuth/cloud popup flow breaks: `COOP: same-origin` severs the
    `window.opener` relationship and COEP blocks cross-origin embeds.
  - iOS Safari's SAB history is uneven.
  Threads solve the architecture elegantly but at a networking/integration
  cost that is antithetical to our cross-origin-CDN + OAuth design.
- Note: OffscreenCanvas/rendering on a worker does **not** need SAB (transfer
  via `postMessage`), but the *blocking loop* still can't block without shared
  memory — so "worker for rendering only" doesn't address the ASYNCIFY
  question at all. "Wasm Workers" (lighter than pthreads) hit the same
  SAB/COOP gate.

### D. Rewrite the loops to be re-entrant — invert control ("no magic")
Make each engine's loop a state machine that returns to a top-level
`emscripten_set_main_loop` callback every frame. This is the literal form of
the "hold on the render frame" instinct.
- **Infeasible at ScummVM scale: 125 engines**, each with hand-written,
  deeply-nested blocking loops and inner blocking waits. Upstream would not
  accept per-engine web-specific loop rewrites, and it would be a permanent
  maintenance tax on every engine. ASYNCIFY was chosen precisely because it is
  the *only* option needing zero engine changes.

## Answering the specific questions

- **Do we need threads?** No — and we actively don't want them here. Threads
  (C) are the "clean, no-ASYNCIFY" path, but the COOP/COEP requirement is
  fundamentally incompatible with the cross-origin CDN + OAuth architecture
  (we hit this once already). Reject.
- **Options without threads?** To yield from a blocking loop without threads
  and without rewriting 125 engines, some form of stack-switching is
  mandatory. The only variables are: compiler-instrumented (ASYNCIFY, today)
  vs VM-native (JSPI, when Safari ships). D (rewrite) is the only genuinely
  ASYNCIFY-free no-thread option and it's not viable.
- **Can the render/input/timer abstraction "hold" the frame?** It's the right
  place to yield, and it's what makes the ASYNCIFY→JSPI swap cheap — but it
  cannot itself replace the stack unwind. Its value is strategic, not a
  mechanism (see below).
- **A middle path within A:** we can't invert control, but we *can* make the
  single yield point smarter — align `delayMillis` to rAF cadence, coalesce
  timer pumps, one present per frame. We've done pieces (the
  `msecs==0 && <20ms → return` throttle, cooperative `checkTimers`). This
  reduces ASYNCIFY jank/cost; it does not remove ASYNCIFY.

## Recommendation

1. **Stay on ASYNCIFY now.** It's the only option covering iOS Safari without
   COOP/COEP. Keep narrowing/optimizing (done: #39; the rAF-aligned yield is a
   cheap further win).
2. **Treat JSPI as the migration target, and keep the yield points funnelled
   through `OSystem` so the swap stays a link-flag change** (`-sASYNCIFY` →
   `-sJSPI`), not a code rewrite. That funnelling — the abstraction we own — is
   the strategic asset: A and B share identical yield points, so the transport
   underneath is swappable for free. Prototype `-sJSPI` behind a build flag on
   Chrome now; when it's stable, ship dual-variant (JSPI where the browser
   supports it, ASYNCIFY fallback for Safari — two link outputs, one codebase,
   feature-detected at load); go JSPI-only once Safari ships.
3. **Do not pursue threads.** The COOP/COEP tax breaks the CDN and OAuth flows
   by design.

## Adversarial / falsification notes

- "Own the abstraction → invert control for free" is the tempting wrong turn.
  The abstraction picks the suspend point; it can't remove the suspend. Verify
  by grepping for `emscripten_set_main_loop` (absent) and reading any engine's
  `go()`/`run()` loop (blocks internally, not just at the top).
- JSPI is not zero-cost either — suspends have a runtime cost — but it's
  per-suspend, not per-instrumented-call, and it removes the size blowup. Worth
  measuring on the actual plugins before committing.
- If a future emscripten offers single-threaded blocking without unwinding,
  that's just stack-switching by another name; there is no way to block the
  browser main thread and keep painting.
- Re-check Safari JSPI status before any migration decision (Phase 4 + assigned
  implementer as of late 2025 → could ship within a year).
