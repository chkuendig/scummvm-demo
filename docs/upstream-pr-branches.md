# ScummVM upstream branch set

The current demo source pin is `5d1f77a50663947424f746c18694b87c405ffedf`. SDL emits right-stick joystick axes while retaining its established mouse-emulation response. Mouse-emulation mappings use the original movement delta, acceleration, sensitivity and subpixel accumulation; native joystick mappings use the normal axis position. The keymapper combines X/Y into one mouse movement and honors remapping. Hardware/iOS velocity mappings and the harmonized touch switching and availability policy remain.

The source change is on `upstream/touch-controls` at `c17a821481e68377d78b02c30140ee5d0fad37ce`. HPL1's existing right-stick bindings need no additional engine-specific changes. All 417 native tests pass, including five real-keymap regressions and the mixed touch/hardware event regression. The 1,728 actual-code SDL/keymapper/HPL1 traces exactly match the pre-conversion mouse and camera input, including different input batching. Twenty-one native-axis checks pass. Recorder version 3 preserves the additional data, with 100 round trips and 100 version-2 compatibility cases passing; SDL2, SDL3 and recorder-enabled syntax checks pass.

Build and deployment are pending. The last successful deployment remains [the mouse-response restoration](https://github.com/chkuendig/scummvm-demo/actions/runs/39307181167), from demo `649a203d2ce497c3aacb35166d141112533523be` and source `681a3f02263f4f28e181587d26eac2b52e674787`. Physical-device feel has not been tested.

The previous demo source pin was `a61201a6eb3deef1626722dc4336e04f06a58cb1`. It includes an HPL1 fix for right-stick camera movement being erased by zero-delta cursor-warp and button events. Mouse motion now accumulates within each input update. The original failure was reproduced with the real HPL1 mouse implementation; held input, quarter/half/full deflection in all four directions, batched motion, buttons, frame reset and neutral-release checks pass. The fix is on `upstream/hpl1-webgl` at `f323d26895b2e519795277914784fb8b0424f7d9`. The [full build and deployment](https://github.com/chkuendig/scummvm-demo/actions/runs/39249588450) passed from demo commit `c4a12bd2fd5d640da58afa0379e31394610d078e`, and live provenance matched that deployment’s source pin. An emulated-touch browser rendered Penumbra’s setup/main menus and intro, and activated menu choices through the on-screen confirm button, with no page errors or failed requests. First-level loading did not finish within the bounded browser check; in-game camera response and physical-device feel remain unverified there. The native regression harness verifies that quarter/half/full stick movement reaches the real HPL1 mouse consumer without being erased.

The previous demo source pin was `ccab4f0fe3d6b4e784430884900dbd755aa0fe4a`. It includes SDL analog right-stick events (`b1aeeac29935bc5f1852de0273008a738c4dc034`) and HPL1 keymaps using shared virtual-mouse action constants (`266a6e1c4bb284c1361b3b6accde99b0f2d635ee`). Axis-range, saturation, DPI, hold, release/cancel and camera-consumer checks passed, along with SDL2/SDL3/HPL1 syntax checks. The [full build and deployment](https://github.com/chkuendig/scummvm-demo/actions/runs/39218144935) succeeded from demo commit `da1dc33f17076ebbbe48e90060ce9a253dbee833`, and live build provenance matches this pin. An emulated-touchscreen browser rendered Grim Fandango, held and released the floating right stick with its knob clamped to the stick radius, and switched to touchpad mode without page errors or failed requests. Physical-device testing remains unverified.

The demo source integration was rebased, preserving merges, onto ScummVM upstream master `f631a289b7137cf324e0032db9b87c0af26271e9` on 2026-10-19. Touch-controls cleanup `a96d92559e76a7fefe2953b60547510716b327be` was cherry-picked as `a11aa5f098b2024d94c7f32cf89bc67ea4c55972` and both branches were pushed. That integration was the previous demo source pin. Its [manual build and deployment](https://github.com/chkuendig/scummvm-demo/actions/runs/39171216016) succeeded, with matching live build provenance at the time.

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

Full Asyncify imports are used for plugin builds, including release builds. The narrowed import list had omitted recorder/plugin imports. The current demo omits `--enable-eventrecorder`; recorder-enabled deployments below are historical.

## AI attribution

The repository's [AI-GUIDELINES.md](../scummvm/AI-GUIDELINES.md) requires commit-message disclosure with `Assisted-by: AGENT_NAME:MODEL_VERSION` and prohibits AI authorship or co-authorship. The prepared commits preserve Christian Kündig as author and record assistance in trailers. Historical model labels were preserved from existing metadata; no AI co-author trailers remain. Human contributors remain responsible for review and testing.

## Validation and deployment

For the 2026-10-19 source refresh, all five touch-policy tests passed. SDL2, SDL3 and GUI syntax checks passed on the combined integration, as did Emscripten build-script shell syntax and theme-archive/source consistency. Seven focused SDL3 hotplug cases passed on the touch-controls branch. The subsequent [manual workflow](https://github.com/chkuendig/scummvm-demo/actions/runs/39171216016) built and deployed all engines successfully. An emulated-touchscreen browser rendered Grim Fandango with the on-screen pad and switched to touchpad mode, with no page errors or failed requests. Physical-device tests remain unverified. The older deployment evidence below records the previous integration.

Use the [game-library Grim launch](https://scummvm.kuendig.io/scummvm.html#--path=/data/games/grim-win-demo1-en%20grim:grim) for testing. The pre-added launcher entry still points to an obsolete `grimdemo` subfolder.

The previous deployed integration was `demo/upstream-integration` at `de7b4e39851d0111ec7e3f1165fd9c2997ee9419`, based on `71cb05b1c03aa6bdcd34f78c20cef12c10067ba5`, combining all five branches. `git diff --check`, shell syntax checks, the Asyncify audio-guard fixture test, JavaScript syntax/logic checks, and verification of the replacement source archive passed. The [final build and deployment](https://github.com/chkuendig/scummvm-demo/actions/runs/37308666206) succeeded. Live build-info matches demo commit `cae236857f07589dece40df3c606fad6e798ada9`, integration `de7b4e39851d0111ec7e3f1165fd9c2997ee9419`, upstream base `71cb05b1c03aa6bdcd34f78c20cef12c10067ba5`, all five then-current branch tips, and `eventRecorder=true`.

The Add Game trap was not reproduced organically in live browser testing; browsing into `/data` produced no JavaScript exceptions or failed requests. A stress scan did produce an HTTP 429 and fatal dialog; its proposed transient-request retry is intentionally excluded from this deployment until it is compiled and exercised. The golden event-recorder replay passed against the final live integration: it loaded `ftdemo.r00`, fetched the Full Throttle demo files, and passed one framebuffer MD5 check with no mismatches, page errors, or failed requests. The dedicated event-recorder workspace remains available for follow-up investigations.

No iOS build, cloud-account gameplay test, physical touch/controller test, or HPL1 gameplay test has been completed for this refreshed branch set. The successful deployment build and emulated-touch browser smoke validate the combined integration; those platform-specific checks remain outstanding.

## Review commands

```sh
git -C scummvm diff upstream/master...upstream/emscripten-runtime
git -C scummvm diff upstream/emscripten-runtime...upstream/cloud-streaming
git -C scummvm diff upstream/master...upstream/touch-controls
git -C scummvm diff upstream/emscripten-runtime...upstream/hpl1-webgl
git -C scummvm diff upstream/emscripten-runtime...upstream/emscripten-recorder
```

The live [demo](https://scummvm.kuendig.io/scummvm.html) and its [build provenance](https://scummvm.kuendig.io/build-info.json) identify the deployed source and all five branch tips. See the JSON manifest for exact SHAs, current publication state and test evidence.
