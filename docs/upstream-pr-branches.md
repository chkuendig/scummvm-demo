# ScummVM upstream branch set

The runtime series is split into filesystem work, standalone browser features, and update/cleanup work. All eight branches below are pushed. The former `upstream/emscripten-runtime` and `upstream/emscripten-url-reload` branches are retired; their old tips and original commit mappings are retained in local backup branches and the JSON history.

Counts are relative to each review base. Every review series has at most five commits, and no branch exceeds ten commits even including its stacked prerequisites. The common source base remains `71cb05b1c03aa6bdcd34f78c20cef12c10067ba5`.

| Branch | Review base | Commits | Including prerequisites | Scope |
| --- | --- | ---: | ---: | --- |
| `upstream/emscripten-update-cleanup` | `upstream/master` | 3 | 3 | SDK/dependencies, JS extraction, browser and URL reload fixes, WebGL and audio handling |
| `upstream/emscripten-filesystem` | `upstream/emscripten-update-cleanup` | 3 | 6 | HTTP ranges and VFS streaming/cache, drag/drop/ROM import and persistent settings |
| `upstream/emscripten-printing` | `upstream/emscripten-update-cleanup` | 1 | 4 | Download game print-outs through the browser |
| `upstream/emscripten-loading-progress` | `upstream/emscripten-update-cleanup` | 1 | 4 | Wasm download and initialization progress |
| `upstream/cloud-streaming` | `upstream/emscripten-filesystem` | 3 | 9 | Stream cloud providers through the shared VFS |
| `upstream/hpl1-webgl` | `upstream/emscripten-update-cleanup` | 5 | 8 | GLES rendering/shaders, menu navigation and native camera input |
| `upstream/emscripten-recorder` | `upstream/emscripten-filesystem` | 4 | 10 | Browser recording/export/replay and viewport-aware controls |
| `upstream/touch-controls` | `upstream/master` | 3 | 3 | Shared touch preferences, controller availability and analog input |

The printing and loading-progress branches depend only on update/cleanup. URL reload is folded into the existing JavaScript/browser cleanup commit. Filesystem work also builds on update/cleanup; cloud streaming and the browser recorder build on the filesystem branch. HPL1 builds on update/cleanup and includes a copy of the shared axis-event/keymapper prerequisite from touch controls. Once that shared support lands upstream, omit the duplicate prerequisite when rebasing HPL1.

The speculative audio-guard test script, unused Asyncify import-list generator and stale import-list JSON are absent throughout every new review series. The actual SDL3 silence/playback/recording guards remain. Both transparency blend changes are now gated by `__EMSCRIPTEN__`, preserving the original native OpenGL behavior. Plugin builds continue to use wildcard Asyncify imports in both release and debug configurations.

The runtime components recombine without merge conflicts. The reorganized runtime source matches the previous published runtime apart from the intentional tooling removals, blend guard, equivalent plugin configuration, module-object ordering and URL listener placement. Touch controls has exactly the previous source tree; HPL1-owned files match the validated input/rendering snapshot. Eight branch diff checks, fourteen C++ syntax checks with cached Emscripten 6.0.2, thirteen unique JavaScript/HTML/shell syntax checks, and both blend-guard preprocessing checks pass. A fresh full SDK build was not run for this history split. The pre-split 429-test suite and 1,728 camera-input comparisons remain recorded in the JSON validation history.

The demo source branch includes the runtime cleanup and SDK 6.0.13 pin at `9e52e845659e3ec37112c5ae37cd52a2aaa44aa3`. The live demo still runs the [previous successful deployment](https://github.com/chkuendig/scummvm-demo/actions/runs/39321081148), from demo `70926e9d42a1c36a21a36bdc623b7730e5848357` and source `d1905802c06d6d3e8487e9e122b2df325b3150f9`. Its five recorded branch tips describe that historical build. This branch maintenance did not redeploy the site. Physical-device gameplay feel remains unverified.

URL reload has been folded into cleanup without adding a commit; dependent branches contain that same existing five-line listener. The demo integration tree is unchanged by this regrouping. The SDK defaults and workflow now target 6.0.13. The bump is folded into the existing update/cleanup SDK commit, and dependent branches are reparented without adding commits. A clean local SDK port build and Asyncify link passed with SDL 3.4.2, FreeType 2.14.3 and libpng 1.6.59. Existing audio guard patterns matched all four generated callbacks and remained idempotent. The [full SDK validation build](https://github.com/chkuendig/scummvm-demo/actions/runs/39426597295) passed with all deployment jobs skipped. The [upgrade record](emscripten-6.0.13-upgrade.md) tracks browser validation before deployment. The live site remains on 6.0.11.

Review each branch against its listed base; the [23 review commits](upstream-pr-commits.md) are listed separately; exact SHAs, original mappings and deployment history are in [upstream-pr-branches.json](upstream-pr-branches.json). For example:

```sh
git -C scummvm diff upstream/master...upstream/emscripten-update-cleanup
git -C scummvm diff upstream/emscripten-update-cleanup...upstream/emscripten-filesystem
git -C scummvm diff upstream/emscripten-update-cleanup...upstream/emscripten-printing
git -C scummvm diff upstream/emscripten-filesystem...upstream/cloud-streaming
```

Human authorship is preserved. Reorganized commits disclose assistance using the repository-required `Assisted-by` trailer. No upstream PRs have been opened by this work.
