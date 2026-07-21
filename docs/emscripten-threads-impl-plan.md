# Implementation plan & test protocol: threaded ASYNCIFY removal

Status: **plan — no work started.** Companion to
`emscripten-asyncify-removal.md` (decision) and
`emscripten-threaded-render.md` (design). Execution order for actually trying
the threads path.

Guiding principle: **fail fast on the two make-or-break risks before investing
in the large work** — (R1) does dynamic-linking + pthreads work for our
MAIN_MODULE + 125 SIDE_MODULE plugin set, and (R2) does iOS Safari stay within
the 640 MB budget with shared memory. Both are probed in the cheap Phase-1
spike. Every phase ends in a go/no-go gate with a concrete test.

## Success criteria (what "worth it" means — decide up front)

- **Primary:** `-sASYNCIFY` removed; main wasm + plugin size measurably down;
  the ASYNCIFY re-entry crash class gone.
- **Must-not-regress:** iOS OOM rate no worse than the current 640 MB build;
  every existing functional test passes; fps ≥ current on reference games.
- **Non-negotiable:** cloud OAuth still works (redirect flow); the
  single-threaded ASYNCIFY build remains available as a fallback for
  non-isolated browsers/users (dual build — no big-bang cutover).
- **Nice-to-have (hand-rolled Phase 3 only):** input latency down (cursor
  tracks pointer), black-bar coordinate fix.

## Phase 0 — Baseline & harness (1–2 days)

Make the before/after falsifiable. Capture, from the current ASYNCIFY deploy:
main wasm size, summed plugin size, boot-to-launcher ms, fps on a 2D ref (COMI)
and a 3D ref (Penumbra scene), iOS device memory high-water, JS heap.

Reuse the existing harness (`scratchpad/pw/` + `tests/replay/`):
`phone-bootcheck.js` (launcher), `ihnm-boot.js`, `replay-test.js`, a Penumbra
scene screenshot. Add three probes: **fps** (sample `frameSeq`/screenshot
cadence over 30 s), **input-latency** (timestamp DOM pointer event → first
frame the cursor moves), **memory** (`performance.memory` + wasm `HEAPU8.length`
sampled, plus a real-device read).

Deliverable: `baseline.json` committed; probes scripted. Gate: none (setup).

## Phase 1 — PROXY_TO_PTHREAD spike (time-boxed 3–5 days, THROWAWAY branch)

Cheapest high-information experiment; front-loads R1 and R2.

Steps:
1. In `configure`, add an `--enable-threads` variant: drop `-s ASYNCIFY=1` on
   main (`configure:3391`) and plugins (`configure:5246`); add
   `-pthread -sPROXY_TO_PTHREAD -sOFFSCREENCANVAS_SUPPORT=1 -sSHARED_MEMORY`;
   plugins get `-pthread`. Keep MAIN_MODULE=1 / SIDE_MODULE=1.
2. Serve with isolation locally: extend `serve.js`/`serve-lan.js` to send
   `COOP: same-origin` + `COEP: require-corp`; serve game data **same-origin**
   for the spike (sidestep the CDN CORP dance) or add
   `Cross-Origin-Resource-Policy: cross-origin` on the `/__cdn` proxy.
3. Boot headless + on a real iPhone.

| # | Test | Pass criterion | Probes which risk |
|---|------|----------------|-------------------|
| P1.1 | Build links | dylink + pthreads links all plugins | **R1** |
| P1.2 | Isolation | `crossOriginIsolated === true` in page | infra |
| P1.3 | Launcher | renders (phone-bootcheck) | R3 (SDL3-threads) |
| P1.4 | 2D game | FT demo / COMI reaches gameplay | R3 |
| P1.5 | Audio | mixer-across-threads produces sound | R3 |
| P1.6 | **iOS memory** | heaviest title (Penumbra/ritter) on a real iPhone stays under budget, no OOM | **R2 (highest)** |
| P1.7 | Size | `-sASYNCIFY` absent; main wasm smaller than baseline | primary |

**Gate G1:** all pass → threads viable, go to Phase 2. iOS OOM (P1.6) or dylink
failure (P1.1) that can't be resolved → **stop the thread path, stay on
ASYNCIFY, wait for JSPI**; document the blocker in the decision doc. This is the
whole point of the spike: a few days buys the go/no-go before any big build.

## Phase 2 — Harden PROXY_TO_PTHREAD to CI-parity (1–2 weeks, if G1 passes)

Steps: all engines/plugins/libs, release mode; real COOP/COEP on deploy (extend
the CI `.htaccess` step) + CDN `Cross-Origin-Resource-Policy` header; **OAuth
redirect flow** replacing the popup; **dual-build loader** — a tiny bootstrap
that feature-detects `crossOriginIsolated` and loads the threaded build, else
the ASYNCIFY build.

Test matrix (headless + device); pass = **parity with `baseline.json`**:

- **Functional:** launcher; FT demo; a 2D game; IHNM (SAGA, the recent work);
  Penumbra 3D scene; recorder-replay CI job; drag-drop ROM import; cloud OAuth
  round-trip (redirect flow).
- **Perf:** fps ≥ baseline on both ref games; boot-to-launcher ≤ baseline + 20 %.
- **Memory:** iOS high-water within budget across the demo game set;
  long-session with the VFS LRU (`vfs_cache_limit`).
- **Robustness:** the `silence_callback` scenario (autoplay-blocked context +
  in-flight chunk download) no longer crashes — should be automatic once
  ASYNCIFY is gone.
- **Cross-browser:** Chrome, Firefox, Safari desktop, **iOS Safari (the gate)**,
  Android Chrome.

**Gate G2:** full matrix at parity → ship-candidate. Any regression → fix, or
fall back to ASYNCIFY-only and shelve.

## Phase 3 — Hand-rolled decoupled presenter (CONDITIONAL)

Only if G2 exposes a need: GL proxying too slow *and* OffscreenCanvas
insufficient, or SDL3-threads too flaky, or we want the render-decoupling wins.
Build per `emscripten-threaded-render.md`, incrementally, each sub-stage
independently testable:

- **3a** shared surface channel + main-thread rAF present (game screen only) →
  game renders via presenter; fps ≥ Phase 2.
- **3b** overlay layer → GUI/launcher composits over game.
- **3c** input ring + coordinate mapping on the presenter → input works; **black-bar
  clip gone** (reuse the portrait recorder-panel tap test).
- **3d** cursor decoupling → measure pointer-to-cursor latency vs Phase 2
  (expect a drop; this is the headline UX win).
- **3e** (optional) AudioWorklet + shared PCM ring → audio; the
  `silence_callback` class is now structurally impossible.

**Gate G3:** decoupling wins measured, parity maintained.

## Phase 4 — Rollout decision

Compare threaded (Phase 2 or 3) vs baseline vs "wait for JSPI" on size, fps,
input latency, iOS memory, maintenance burden, cross-browser. Outcome is one of:
ship **dual-build** (threaded to isolated-capable sessions, ASYNCIFY fallback
otherwise), or shelve with the spike/hardening results recorded for the JSPI
revisit. No scenario requires a big-bang cutover.

## Test harness reference

| Probe | Script | Metric | Pass |
|-------|--------|--------|------|
| Launcher boot | `phone-bootcheck.js` | rendered + `errors:[]` | render, no errors |
| 2D gameplay | `ihnm-boot.js` (parametrized) | rich frame reached | title/gameplay frame |
| 3D scene | Penumbra shot | scene renders | visual match |
| Recorder replay | `tests/replay/replay-test.js` | `Check screenshot result` | success, no fail |
| fps | new fps probe | frames/30 s | ≥ baseline |
| input latency | new latency probe | pointer→cursor ms | ≤ baseline (Phase 3: <) |
| memory | new probe + device | wasm+JS heap high-water | within iOS budget |
| isolation | inline | `crossOriginIsolated` | true (threaded build) |

Node: `dists/emscripten/emsdk-4.0.15/node/.../node`; range-correct server:
`tests/replay/serve.js` (add COOP/COEP for threaded runs).

## Rollback / coexistence

The dual build is the safety net: ASYNCIFY stays the default and the fallback;
the threaded build is served only to isolated-capable sessions, selected by the
loader. If the threaded build regresses in the field, flip the loader default
back to ASYNCIFY — no redeploy of game data, no user-visible break.

## Risk register (front-loaded into the spike)

| ID | Risk | Probed at | If it fails |
|----|------|-----------|-------------|
| R1 | dylink + pthreads links our plugin set | P1.1 | stop; wait for JSPI |
| R2 | iOS memory under shared memory vs 640 MB | P1.6 | stop; wait for JSPI |
| R3 | SDL3-emscripten threaded GL/event/audio maturity | P1.3–1.5 | go hand-rolled (Phase 3) |
| R4 | OAuth under `COOP: same-origin` | Phase 2 | redirect flow / separate auth origin |
| R5 | upstream accepts a threaded backend | Phase 4 | keep as a downstream/demo-only variant |
