# Production monitoring (Sentry) — rollout plan & runbook

Crash monitoring + WebAssembly symbolication for the Emscripten demo
(`scummvm.kuendig.io`). Researched & verified 2026-07; see "Findings" at the end.

## Verdict

Sentry **does** symbolicate Emscripten-generated wasm today, and the wasm
integration is actively maintained (`@sentry/wasm` v10.43.x, 2026). The chain is:

```
build with -gseparate-dwarf  ->  build_id UUID in the shipped wasm (native, LLVM>=17)
   ->  sentry-cli debug-files upload (the fat sidecar .debug.wasm)  ->  Sentry
   ->  @sentry/wasm wasmIntegration() rewrites frames to module+addr+debug-id
   ->  Sentry matches addr -> DWARF -> function/file:line
```

## ⚠️ VERIFIED: `-Wl,--build-id` is mandatory (Phase 1 result)

Despite clang 22, our Emscripten `-gseparate-dwarf` output does **NOT** emit a
`build_id` on its own — `sentry-cli difutil check` reports
`Debug ID: 00000000-...` and **`Usable: no (missing debug identifier)`** for both
the shipped wasm and the debug sidecar. Uploaded debug files would never match
events. Adding **`-Wl,--build-id`** fixes it: the shipped wasm and its
`*.debug.wasm` then share the **same** non-zero Debug ID and both report
`Usable: yes`. Verified for MAIN_MODULE and SIDE_MODULE.

So the required per-module link flags are:
```
-gseparate-dwarf=<name>.debug.wasm  -Wl,--build-id
```
Notes:
- `-gseparate-dwarf` triggers "limited binaryen optimizations" — the shipped
  wasm is slightly less optimized than a pure `-O2` build. This is unavoidable:
  the shipped binary and the DWARF must come from the *same* build for addresses
  to match, so we ship the `-gseparate-dwarf` build (with its build_id), not a
  separately-optimized one.
- The shipped wasm keeps only an `external_debug_info` URL pointer to the debug
  file (we don't host it; a 404 only affects local DevTools, not Sentry, which
  gets it via upload). Optionally blank it with `SEPARATE_DWARF_URL`.

(The research's "build_id native since LLVM 17" claim did not hold for emcc
4.0.15; the `-Wl,--build-id` requirement was found by testing offline.)

## Key facts that shape the design

- **The Loader/base Browser SDK cannot symbolicate wasm.** `wasmIntegration()`
  lives in a separate `@sentry/wasm` package and must be wired into `Sentry.init`.
  => switch the injected Loader to a bundled `@sentry/browser` + `@sentry/wasm`.
- **The crash is in a plugin (`libhpl1.so`), a SIDE_MODULE.** Every side module is
  a standalone wasm with its **own** DWARF/build_id and must be split + uploaded
  **independently**. Upstream Emscripten docs say nothing about symbolicating side
  modules — this is the least-proven part, so it is verified first (Phase 1).
- **`-gseparate-dwarf` keeps the shipped wasm lean** (just an external-debug-info
  URL pointer; customizable via `SEPARATE_DWARF_URL`), but the sidecar
  `*.debug.wasm` is a **full copy of the program + DWARF, ~an order of magnitude
  larger** than the wasm. Never ship it inline; only upload it to Sentry.
  (It is gitignored via `*.debug.wasm`.)
- **`-O2`/`-Oz` degrade symbolication** (inlining, reordering, name stripping).
  Production `-O2` frames are lossy-but-useful (function-level, approximate).
  For crisp frames in the crashing plugin, optionally build `hpl1` at `-O1`/`-Og`.
- **OOM must be forced to a catchable abort.** `ALLOW_MEMORY_GROWTH=1` (which we
  use) flips `ABORTING_MALLOC`'s default to **0**, so a failed alloc returns NULL
  instead of aborting. Set **`-sABORTING_MALLOC=1`** so OOM -> `abort()` ->
  `Module.onAbort` -> catchable JS exception -> Sentry. Combined with our lowered
  `MAXIMUM_MEMORY`, this converts the otherwise-uncatchable iOS Safari device-OOM
  tab-kill into a reported issue.

## Secrets / config (`.env`, gitignored; mirror to GitHub)

| Key | Where | Notes |
|-----|-------|-------|
| `SENTRY_AUTH_TOKEN` | GH **secret** + `.env` | scopes: `project:read,project:releases,org:read,event:read` |
| `SENTRY_ORG` / `SENTRY_PROJECT` | GH **variable** + `.env` | slugs |
| `SENTRY_DSN` | GH **variable** + `.env` | public client key |
| `SENTRY_ENVIRONMENT` | GH **variable** | `production` |
| `SENTRY_URL` | `.env` only | blank = SaaS; set for self-hosted GlitchTip |

## Rollout phases

**Phase 0 — credentials.** Create the Sentry project + auth token; fill `.env`;
add GH secret/variables. (No strong non-Sentry alternative surfaced; GlitchTip is
a Sentry-protocol-compatible self-host option using the same SDK.)

**Phase 1 — prove the toolchain offline (no account needed). ✅ DONE.** Verified
that `-gseparate-dwarf -Wl,--build-id` yields matching, `Usable: yes` debug files
for both MAIN_MODULE and SIDE_MODULE via `sentry-cli difutil check` (see the
"VERIFIED" section above). `-Wl,--build-id` is required.

**Phase 2 — client capture.** Replace the Loader injection with a bundled init
(`sentry-init.js`, injected like the loader): DSN, `release=<wasm-hash>`, `dist`,
env, `wasmIntegration()`; hook `Module.onAbort` -> `captureException` (OOM),
`webglcontextlost` -> `captureMessage`; `beforeSend` attaches memory context
(heap size, `performance.memory`, launched game).

**Phase 3 — CI: build + upload.** `-gseparate-dwarf` + `-sABORTING_MALLOC=1` for
main module **and** plugins; emit JS source map. New job "Upload debug info": for
each wasm (main + every plugin) `sentry-cli debug-files upload`; upload source
maps; `sentry-cli releases new/set-commits/finalize` using the wasm hash. Gate on
`SENTRY_AUTH_TOKEN` (no-op if unset, like the existing loader step).

**Phase 4 — verify end-to-end.** Trigger a test throw + the real OOM; confirm a
symbolicated issue with plugin frames.

## Findings (verified, high-confidence)

1. `@sentry/wasm` `wasmIntegration()` is required and separate from the base/Loader SDK; maintained in 2026.
2. Symbolication needs uploaded debug files matched by a `build_id` UUID custom section present in both shipped + debug wasm.
3. `build_id` is native since LLVM 17 (we're on clang 22); else Sentry `wasm-split` injects it.
4. Each SIDE_MODULE plugin needs independent split + upload; not covered by Emscripten docs (least-proven).
5. `-gseparate-dwarf` sidecar is a full program copy — upload only, never ship.
6. `-O2/-Oz` degrade DWARF fidelity; frames are lossy above `-O1`.
7. `ABORTING_MALLOC` (flipped to 0 by `ALLOW_MEMORY_GROWTH`) must be forced to 1 so OOM aborts catchably via `Module.onAbort`.

## Queued for AFTER the Sentry rollout (tracked as tasks 31-33)

1. **Move cache-busting out of the scummvm submodule into the super-repo CI.**
   The `scummvm.js?v=<wasm-hash>` stamp currently lives in scummvm's
   `emscripten.mk`; move it to `main.yml` (deploy-demo). NOTE: `main.yml:218`
   (`echo AddType... > .htaccess`) **overwrites** the build's `.htaccess`, which
   silently clobbered the Cache-Control `.htaccess` (so it was never really
   tested). Fold Cache-Control into that line instead, then re-verify LiteSpeed.
2. **Remove the HPL1 ETC2 compression work** (revert commit `d96da5700a8`:
   `SDLTexture.cpp/.h`, `rg_etc1.cpp/.h`, `module.mk`). Keep the glGetError
   gating. ETC2 didn't fix the crash (MAXIMUM_MEMORY=512MB did).
3. **Offload in-memory IO** to browser HTTP cache / IndexedDB to cut wasm-heap
   pressure, keeping settings + savegames durable (no eviction). Design from the
   FS investigation.
