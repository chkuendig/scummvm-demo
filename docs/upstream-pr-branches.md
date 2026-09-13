# ScummVM upstream branch set

Prepared from deployment source on 2026-09-13; revised to put Emscripten runtime first and cloud streaming second. The five branches are in the **`scummvm/` submodule**, based on upstream master `2085bcb368c19bc90f0190efcd56b9d58cd7fb5a`.

Runtime and cloud have been pushed to `chkuendig/scummvm`; touch, HPL1, and recorder remain local. No PRs have been opened. The demo is now pinned to `demo/upstream-integration`, which combines all five branches. Its deployment build enables the event recorder.

## Suggested opening order

| Order | Branch | Review base | Own commits / files |
| --- | --- | --- | --- |
| 1 | `upstream/emscripten-runtime` | `upstream/master` | 33 / 45 |
| 2 | `upstream/cloud-streaming` | `upstream/emscripten-runtime` | 6 / 23 |
| 3 | `upstream/touch-controls` | `upstream/emscripten-runtime` | 5 / 46 |
| 4 | `upstream/hpl1-webgl` | `upstream/emscripten-runtime` | 9 / 41 |
| 5 | `upstream/emscripten-recorder` | `upstream/emscripten-runtime` | 5 / 13 |

Runtime is the foundation. Branches 2–5 each depend only on runtime and can be reviewed separately after it lands. Cloud streaming does not block touch, HPL1, or recording.

[Runtime diff on GitHub](https://github.com/chkuendig/scummvm/compare/2085bcb368c19bc90f0190efcd56b9d58cd7fb5a...upstream/emscripten-runtime) · [Cloud diff on GitHub](https://github.com/chkuendig/scummvm/compare/0c5737e1460024ad2a824161f71381d6db4f2f61...upstream/cloud-streaming)

## Suggested PR titles and descriptions

### 1. EMSCRIPTEN: Stream HTTP game data and update the browser runtime

Add the shared virtual filesystem, HTTP range streaming, loading progress, bounded cache memory, persistent browser storage, drag-and-drop file and ROM import, browser printing, and JavaScript library integration for backend services. Include HTTP 206 response handling and download progress in SessionRequest, which the HTTP reader requires.

Update Emscripten to 6.0.2 with the dependency fixes, WebGL2 defaults and fallback handling, memory limits, release-only Asyncify import narrowing, SDL3 audio re-entry guard, and the small SCUMM conditional-compilation warning fix.

The browser OAuth callback and trusted-origin filter stay with the browser JavaScript integration. The shared cloud storage APIs and existing cloud filesystem stay at upstream's implementation in this branch; its HTTP streaming code does not depend on the new cloud APIs.

### 2. CLOUD: Add range downloads and browser cloud streaming

Add range downloads to cloud providers, cache OneDrive download URLs, handle token-refresh failures, centralize access-token access, and fix Box refresh handling in the browser. Connect the cloud filesystem to the shared virtual filesystem introduced by runtime, including chunked reads and folder-cache invalidation when the account changes. Update the browser Cloud tab to reflect direct access to cloud files.

This branch includes the provider APIs and the cloud adapter that consumes them. Its diff contains 23 files, separate from the HTTP, SDK, graphics, and browser file-import changes in runtime.

### 3. SDL: Add shared touch presets and on-screen controls

Expose touch presets for menus, 2D games, and 3D games through the shared Control tab, and align iOS with those settings. Add SDL on-screen mode switching and an analog gamepad, including physical-controller fallback and session-persistent manual mode changes. Include the layouts and regenerated theme bundles.

### 4. HPL1: Add GLES rendering and controller-friendly menus

Run HPL1 using a GLES renderer and compatible shaders on the Emscripten WebGL2 backend. Bundle shader resources for generated projects and add controller bindings, menu focus navigation, and the related rendering and menu lifetime fixes.

### 5. EMSCRIPTEN: Support event recording and replay

Make recording and replay work with SDL3 and the Emscripten timer manager, preserve network polling when recorder modes change, and exclude HTTP waits from the recording timeline. Finalize buffered recordings correctly and provide accessible browser download and recorder controls on letterboxed displays.

The integration demo enables `--enable-eventrecorder`. Recorder builds use the full Asyncify import list, including release builds: the narrowed list was generated without recorder support.

## AI attribution

The repository's [AI-GUIDELINES.md](../scummvm/AI-GUIDELINES.md) and [published policy](https://github.com/scummvm/scummvm/blob/master/AI-GUIDELINES.md) require commit-message disclosure using `Assisted-by: AGENT_NAME:MODEL_VERSION` and prohibit AI authorship or co-authorship. Human contributors retain responsibility for understanding, reviewing, and testing their submissions.

All 58 pending commits retain Christian Kündig as author and disclose this branch-preparation assistance with `Assisted-by: Codex:GPT-6`. Twelve historical Claude co-author trailers were converted into `Assisted-by: Claude:Opus-4.8` or `Assisted-by: Claude:Fable-5`, preserving the model labels already recorded in those commits. No unrecorded historical model was inferred. Basic tools such as Git and the compiler are not listed in the trailers.

Every pending commit was checked with Git's trailer parser. There are no AI co-author trailers in the prepared branch set. This metadata records assistance; it does not certify human review or a complete gameplay test.

## Reviewing and rebasing

From this repository:

```sh
git -C scummvm diff upstream/master...upstream/emscripten-runtime
git -C scummvm diff upstream/emscripten-runtime...upstream/cloud-streaming
git -C scummvm diff upstream/emscripten-runtime...upstream/touch-controls
git -C scummvm diff upstream/emscripten-runtime...upstream/hpl1-webgl
git -C scummvm diff upstream/emscripten-runtime...upstream/emscripten-recorder
```

After runtime lands, use its recorded tip as the boundary to move each dependent branch onto upstream master. This also handles a squash merge. In a clean ScummVM worktree:

```sh
git fetch upstream master
git rebase --onto upstream/master 0c5737e1460024ad2a824161f71381d6db4f2f61 upstream/cloud-streaming
git rebase --onto upstream/master 0c5737e1460024ad2a824161f71381d6db4f2f61 upstream/touch-controls
git rebase --onto upstream/master 0c5737e1460024ad2a824161f71381d6db4f2f61 upstream/hpl1-webgl
git rebase --onto upstream/master 0c5737e1460024ad2a824161f71381d6db4f2f61 upstream/emscripten-recorder
```

Use a separate worktree when building or switching branches; the deployment checkout contains local build artifacts.

## Deployment provenance and coverage

The original [verified successful deployment run](https://github.com/chkuendig/scummvm-demo/actions/runs/29839172807) used demo commit `e95a2d90fb1890856ba6338df035499c6f048d99`, pinning ScummVM to `c663ad7ab10ad669c8b6d9941f1f3814ba4c2486`. The live HTML matched its archived page byte-for-byte when checked: SHA-256 `2ab613330c16c07ee7913684025665aabbcdc6e501b4839c1dd1b6498901eb36`, Sentry release `194fa8f51e44`.

All 54 downstream source commits are accounted for: 53 are included, and the SAGA commit is excluded at the user's request. SAGA re-release detection is already upstream in `e03be5eb96e`; the residual missing-patch resource guard was dropped and its branch deleted.

Mixed source changes were separated where needed:

- `c8f59745e29`: HTTP SessionRequest support into runtime; provider range APIs into cloud.
- `8172967ea2b`: generic VFS and HTTP streaming into runtime; cloud adapter, cache invalidation, module entry, and Cloud-tab changes into cloud.
- `3b6856a341e`: SDL/session settings into touch; recorder coordinate mapping and panel layout into recording.
- `e6a55a293df`: virtual-keyboard default into runtime; HPL1 shader packaging into HPL1.

Rebasing preserved upstream's cloud-header override cleanup and IHNM detection fix. The touch branch uses theme version 0.9.25 and regenerated bundles containing both upstream and touch layouts. Whitespace cleanup was folded into the commits that introduced those lines.

The demo catalogue, assets, hosting workflows, Sentry integration, cloud-service repository, icons, and future threading/multiplayer notes remain outside these ScummVM branches. The demo-only cloud-host substitution remains in the hosting workflow.

[The manifest](upstream-pr-branches.json) records exact tips, bases, source assignments and exclusions, publication state, and validation evidence.

## Validation

- The runtime/cloud split preserved the combined source tree. All five branches were then rebased onto upstream `2085bcb368c`; each rebased tree exactly matched merging upstream into its previous tip. The only subsequent source change is the recorder Asyncify configuration fix.
- All branches merge together without conflicts; each review diff and every individual commit passes `git diff --check`.
- All 58 commits passed the attribution audit: human authors preserved, recognized `Assisted-by` trailers, and no AI co-authors.
- Before the latest upstream refresh, twenty-one C++ translation units passed Emscripten Clang syntax/type checks using the existing generated deployment configuration with `USE_CLOUD` enabled. Checks cover the runtime's existing cloud backend and new HTTP reader, then the new cloud provider APIs, adapter, factory, and options dialog.
- Shell and JavaScript syntax checks passed. The earlier checks of eight JavaScript files, inline shell JavaScript, Asyncify JSON, four theme bundles, and the embedded default theme remain applicable to their unchanged final contents.

The recorder import-selection check passed all four release/debug and recorder-on/off combinations. The C++ checks use `-fsyntax-only`; no full Wasm link, iOS build, or gameplay test has been run for these branches. Before upstream submission, complete the relevant build and gameplay validation and regenerate/validate the release Asyncify import list against the final build configuration.

## Combined demo testing

The ScummVM branch `demo/upstream-integration` at `915ac4310a0e0a7bcda08f8765d2abb4d9c58a8c` contains all five prepared branch tips as ancestors, based on upstream master `2085bcb368c19bc90f0190efcd56b9d58cd7fb5a`. The demo repository pins that exact commit, so the build is reproducible even if the upstream PR branches are rebased again.

Pushing the demo's `main` branch runs the existing Build & Deploy workflow and updates [the demo](https://scummvm.kuendig.io/scummvm.html). The generated [build-info.json](https://scummvm.kuendig.io/build-info.json) identifies the demo commit, ScummVM commit, upstream base, and all five included branch tips. Compare it with this manifest to confirm which build is live.

Suggested browser checks:

1. Runtime: launch a catalogue game, check loading progress, and try file/folder drag and drop.
2. Cloud: connect a provider in the Cloud tab, browse its files, and launch a game from cloud storage.
3. Touch: test the 2D and 3D presets, the on-screen gamepad, and switching to a physical controller.
4. HPL1: launch a supported HPL1 game in WebGL2 and check rendering and menu/controller navigation.
5. Recorder: start a game with `--record-mode=record --record-file-name=test.r00`, stop and download the recording, then replay it. The scheduled replay workflow uses the same submodule revision.

For later refreshes, rebase runtime onto upstream master first, then rebase each sibling from the old runtime tip onto the new one. Rebuild the integration branch by merging cloud, touch, HPL1, and recorder into runtime; update this manifest and the demo gitlink together. Keep the integration branch out of upstream PRs.

The existing golden replay job timed out before this refresh because the recording never loaded. A fresh successful deployment is build evidence, not a claim that that replay test or every browser check above has passed.
