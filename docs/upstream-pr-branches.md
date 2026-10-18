# ScummVM upstream branch set

The demo source integration was rebased, preserving merges, onto ScummVM upstream master `f631a289b7137cf324e0032db9b87c0af26271e9` on 2026-10-19. Touch-controls cleanup `a96d92559e76a7fefe2953b60547510716b327be` was cherry-picked as `a11aa5f098b2024d94c7f32cf89bc67ea4c55972` and both branches were pushed. The demo submodule points to that integration. A subsequent [manual build and deployment](https://github.com/chkuendig/scummvm-demo/actions/runs/39171216016) succeeded, and the live build provenance matches the pinned source.

The five source branches live in the `scummvm/` submodule. The original branch set was prepared from the deployed integration on upstream base `71cb05b1c03aa6bdcd34f78c20cef12c10067ba5` on 2026-10-05. No upstream PRs have been opened.

## Suggested PR order

| Order | Branch | Review base | Scope |
| --- | --- | --- | --- |
| 1 | `upstream/emscripten-runtime` | `upstream/master` | Shared Emscripten runtime, streamed VFS, SDK update, Asyncify configuration and loading progress |
| 2 | `upstream/cloud-streaming` | runtime | Range downloads and cloud filesystem streaming |
| 3 | `upstream/touch-controls` | `upstream/master` | Touch presets, on-screen controls and controller switching |
| 4 | `upstream/hpl1-webgl` | runtime | HPL1 WebGL2 rendering, shaders and controller-friendly menus |
| 5 | `upstream/emscripten-recorder` | runtime | Browser event recording, replay and timer integration |

Runtime is the foundation for cloud streaming, HPL1 WebGL and the recorder. Touch controls now has an independent upstream base. The demo contains rebased copies of the original branch commits plus the touch-controls cleanup; the source branches retain their own histories. Branch heads, commit lists, file counts and exact bases are recorded in [upstream-pr-branches.json](upstream-pr-branches.json).

## Runtime details

The runtime branch includes the browser loading-progress correction: the fill now tracks the downloaded-byte text without a lagging CSS transition, and unknown or zero content lengths avoid invalid percentages. It also includes the SDL3 audio callback Asyncify guard. The Add Game exception was not reproduced during live browsing; a live-code A/B probe verified the guard returns before a callback enters wasm while Asyncify is suspended. The transient HTTP retry change remains deferred because its C++ implementation has not yet been compiled or runtime-tested.

The Emscripten dependency script now downloads a52dec 0.7.4 from Debian's original source archive and verifies its SHA-256 before extraction. The prior VideoLAN endpoint returned an Anubis challenge page to GitHub Actions. The separate libmpeg2 URL, pinned to commit `946bf4b5…`, returned a valid archive during this refresh, so it remains pinned to that source rather than substituting Debian's older 0.5.1 package.

Full Asyncify imports are used for plugin builds, including release builds. The narrowed import list had omitted recorder/plugin imports. The demo enables `--enable-eventrecorder` and uses the full list.

## AI attribution

The repository's [AI-GUIDELINES.md](../scummvm/AI-GUIDELINES.md) requires commit-message disclosure with `Assisted-by: AGENT_NAME:MODEL_VERSION` and prohibits AI authorship or co-authorship. The prepared commits preserve Christian Kündig as author and record assistance in trailers. Historical model labels were preserved from existing metadata; no AI co-author trailers remain. Human contributors remain responsible for review and testing.

## Validation and deployment

For the 2026-10-19 source refresh, all five touch-policy tests passed. SDL2, SDL3 and GUI syntax checks passed on the combined integration, as did Emscripten build-script shell syntax and theme-archive/source consistency. Seven focused SDL3 hotplug cases passed on the touch-controls branch. The subsequent [manual workflow](https://github.com/chkuendig/scummvm-demo/actions/runs/39171216016) built and deployed all engines successfully. An emulated-touchscreen browser rendered Grim Fandango with the on-screen pad and switched to touchpad mode, with no page errors or failed requests. Physical-device tests remain unverified. The older deployment evidence below records the previous integration.

Use the [game-library Grim launch](https://scummvm.kuendig.io/scummvm.html#--path=/data/games/grim-win-demo1-en%20grim:grim) for testing. The pre-added launcher entry still points to an obsolete `grimdemo` subfolder.

The previous deployed integration was `demo/upstream-integration` at `de7b4e39851d0111ec7e3f1165fd9c2997ee9419`, based on `71cb05b1c03aa6bdcd34f78c20cef12c10067ba5`, combining all five branches. `git diff --check`, shell syntax checks, the Asyncify audio-guard fixture test, JavaScript syntax/logic checks, and verification of the replacement source archive passed. The [final build and deployment](https://github.com/chkuendig/scummvm-demo/actions/runs/37308666206) succeeded. Live build-info matches demo commit `cae236857f07589dece40df3c606fad6e798ada9`, integration `de7b4e39851d0111ec7e3f1165fd9c2997ee9419`, upstream base `71cb05b1c03aa6bdcd34f78c20cef12c10067ba5`, all five then-current branch tips, and `eventRecorder=true`.

The Add Game trap was not reproduced organically in live browser testing; browsing into `/data` produced no JavaScript exceptions or failed requests. A stress scan did produce an HTTP 429 and fatal dialog; its proposed transient-request retry is intentionally excluded from this deployment until it is compiled and exercised. The golden event-recorder replay passed against the final live integration: it loaded `ftdemo.r00`, fetched the Full Throttle demo files, and passed one framebuffer MD5 check with no mismatches, page errors, or failed requests. The dedicated event-recorder workspace remains available for follow-up investigations.

No iOS build, cloud-account gameplay test, physical touch/controller test, or HPL1 gameplay test has been completed for this refreshed branch set. The deployment build and browser smoke will add evidence for the combined integration, not replace those platform-specific checks.

## Review commands

```sh
git -C scummvm diff upstream/master...upstream/emscripten-runtime
git -C scummvm diff upstream/emscripten-runtime...upstream/cloud-streaming
git -C scummvm diff upstream/master...upstream/touch-controls
git -C scummvm diff upstream/emscripten-runtime...upstream/hpl1-webgl
git -C scummvm diff upstream/emscripten-runtime...upstream/emscripten-recorder
```

The live [demo](https://scummvm.kuendig.io/scummvm.html) and its [build provenance](https://scummvm.kuendig.io/build-info.json) identify the deployed source and all five branch tips. See the JSON manifest for exact SHAs, current publication state and test evidence.
