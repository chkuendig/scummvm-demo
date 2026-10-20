# ScummVM upstream branch set

All nine review branches and the consolidated demo source are pushed and based on upstream `ed949213a23440447ea402e263daa871394b6bf9`. The former monolithic runtime and URL-reload branches remain retired.

| Branch | Review base | Own commits | Including prerequisites | Scope |
| --- | --- | ---: | ---: | --- |
| `upstream/emscripten-update-cleanup` | `upstream/master` | 4 | 4 | SDK/dependencies and separate WebMIDI, speech and browser JavaScript libraries |
| `upstream/emscripten-opengl` | `upstream/master` | 1 | 1 | WebGL2 context selection, availability/surface fallback, browser resizing and opaque canvas blending |
| `upstream/emscripten-filesystem` | `upstream/emscripten-update-cleanup` | 3 | 7 | HTTP ranges and VFS streaming/cache, drag/drop/ROM import and persistent settings |
| `upstream/emscripten-printing` | `upstream/emscripten-update-cleanup` | 1 | 5 | Download game print-outs through the browser |
| `upstream/emscripten-loading-progress` | `upstream/emscripten-update-cleanup` | 1 | 5 | Wasm download and initialization progress |
| `upstream/cloud-streaming` | `upstream/emscripten-filesystem` | 3 | 10 | Stream cloud providers through the shared VFS |
| `upstream/hpl1-webgl` | `upstream/emscripten-opengl` | 5 | 6 | GLES rendering/shaders, menu navigation and native camera input |
| `upstream/emscripten-recorder` | `upstream/emscripten-filesystem` | 3 | 10 | Browser recording/export/replay and viewport-aware controls |
| `upstream/touch-controls` | `upstream/master` | 3 | 3 | Shared touch preferences, controller availability and analog input |

Cleanup now has one commit each for WebMIDI, text-to-speech, browser-backend JavaScript and SDK/dependency/build updates. The browser commit also contains URL reload. Its diff contains no engine or OpenGL changes. `upstream/emscripten-opengl` owns WebGL2/ES3 context selection, capability detection and surface fallback, browser-window resizing, and Emscripten-only canvas-alpha preservation. HPL1 builds on that rendering branch.

Filesystem work builds on cleanup; cloud and recorder build on filesystem. The recorder UI changes are folded into its browser recorder feature commit to keep complete stacks within ten commits. The recorder-specific `SDL_GetTicks()` fix remains. HPL1 includes the shared engine-axis support mirrored from touch controls; omit that duplicate prerequisite once the API lands upstream.

The generated-JavaScript audio patching is removed from cleanup, its dependents and the demo. The existing libmad `-fforce-mem` configure patch is retained at user request. The VideoLAN liba52 0.7.4 archive is available again (HTTP 200) and matches the cached archive exactly; its original URL is retained. Pristine libmad 0.15.1b configures with the same `-Oz` flags and all eleven source files compile with SDK 6.0.13. The SCUMM `sound.cpp` warning edit is reverted. The removed audio-test script and obsolete Asyncify import tooling remain absent throughout every review series.

The Emscripten-specific mixer and timer were already merged upstream in `1dccebfb0c2` and `26fa61ad5ee` and remain active. They keep audio mixing/file I/O out of SDL audio callbacks and pump timers cooperatively. The recorder-specific callback fix uses `SDL_GetTicks()` to avoid recorder timer/mixer recursion. The generated-JavaScript guards were not established as necessary for ordinary builds: with all four guards removed, Chromium processed 512 active audio callbacks during main-stack suspension without errors. A separate simulated autoplay-blocked case processed 74 silence callbacks and 389 subsequent active callbacks without errors while browsing HTTP directories. Asyncify reports Normal while the main stack is suspended, so the removed state guards did not block that case.

Nine branch/per-commit diff checks, fourteen unique JavaScript/HTML/shell syntax checks, and six C++ syntax checks with SDK 6.0.13 pass. Library commit scopes and the absence of engine/OpenGL changes in cleanup are checked. The rebase preserves upstream’s FAAD mirror fix and HPL1 Glowstick key fix. The consolidated source retains the cleaned demo integration with exactly the new upstream file updates and includes all nine branch heads in its ancestry.

The consolidated source is `b0354958e1eb74017a98b725a710c3af47556267`. The previous refreshed full build was cancelled while queued because it targeted the preceding revision. This configure review uses a focused SDK 6.0.13 OpenGL-branch build and local browser validation; a full build of the consolidated demo is still pending. The [last successful deployment](https://github.com/chkuendig/scummvm-demo/actions/runs/39470229200) still uses SDK 6.0.13, demo `c8aa6ef69bc7266b21c27bbb305d9dd7c4032c92` and source `9e52e845659e3ec37112c5ae37cd52a2aaa44aa3`. This review refresh has not redeployed the site. Physical-device gameplay feel and Safari/iOS remain untested by these checks.

The [commit list](upstream-pr-commits.md), [manifest and historical provenance](upstream-pr-branches.json), and [SDK upgrade record](emscripten-6.0.13-upgrade.md) contain the exact references. Reorganized commits preserve human authorship and disclose assistance with `Assisted-by`. No upstream PRs have been opened by this work.

The SDK commit explicitly records Emscripten 4.0.10 → 6.0.13 (SDL3 3.4.2, FreeType 2.14.3 and libpng 1.6.59), libtheora 1.1.1 → 1.2.0, and RetroWave e6bf60e → ddb5b34. All `Split-from:` lines have been removed from the 24 review commit messages.

The OpenGL branch is now independent: its single commit is based directly on upstream master and touches only configure, SDL capability/fallback selection, the SDL OpenGL resize path and framebuffer blending. Comparing it against upstream master excludes the SDK update and JavaScript extraction commits. HPL1 retains the same five own commits on top of this branch (six including prerequisites). All 24 review commits are cherry-picked into the refreshed demo, with existing demo-specific changes preserved and all branch heads tracked in its ancestry.

The configure review restores upstream memory flags (128 MiB initial memory, 32 MiB stack, no explicit maximum; SDK default maximum 2 GiB), removes the unsupported iOS memory comment, and shortens the unload/SIGINT comment while retaining `_raise`. The standalone static browser build exposed missing `Module._malloc` and runtime helper exports in cleanup; their upstream export lists are restored, covering the old HTTP filesystem used before the filesystem feature branch. Browser networking uses `window.fetch`, so the Fetch API comment remains. The early unconditional ImGui SDL3 renderer definition is removed from cleanup. The OpenGL branch fixes the real capability check by omitting unrelated `LIBS` during the Emscripten SDL3 probe; this avoids the unavailable `-lvorbisfile` link flag before Emscripten ports are stripped later in configure. Other backends keep their existing probe.

The browser extraction names the state setter `OSystem_Emscripten_setFullscreen`. The filesystem networking commit names the error accessor `NetworkReadStreamEmscripten_getError`; declarations, JavaScript definitions and C++ calls match. Seven JavaScript comparisons confirm unchanged results. Both functions retain C linkage to match the JavaScript library symbols.

A focused build of the independent `upstream/emscripten-opengl` branch enables ImGui through the generic capability check. Local Chromium runs with WebGL disabled and enabled inspect live ImGui backend state in Wasm memory and capture the launcher. This checks actual SDL-renderer fallback, rather than only a successful configure probe. This browser test does not cover physical iOS memory limits.
