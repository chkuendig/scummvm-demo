# ScummVM upstream branch set

All nine review branches are based on upstream `964f9ed828fc8538def571ca25b33d6dfbca1bbc`. Seven start directly on master; cloud streaming stays on filesystem and HPL1 stays on OpenGL, as requested. The ten-commit limit applies above each review base.

| Branch | Review base | Own commits | With prerequisites | Files in review |
| --- | --- | ---: | ---: | ---: |
| [upstream/emscripten-update-cleanup](https://github.com/scummvm/scummvm/compare/master...chkuendig:scummvm:upstream/emscripten-update-cleanup) | `upstream/master` | 8 | 8 | 14 |
| [upstream/emscripten-opengl](https://github.com/scummvm/scummvm/compare/master...chkuendig:scummvm:upstream/emscripten-opengl) | `upstream/master` | 4 | 4 | 4 |
| [upstream/emscripten-filesystem](https://github.com/scummvm/scummvm/compare/master...chkuendig:scummvm:upstream/emscripten-filesystem) | `upstream/master` | 4 | 4 | 28 |
| [upstream/emscripten-printing](https://github.com/scummvm/scummvm/compare/master...chkuendig:scummvm:upstream/emscripten-printing) | `upstream/master` | 1 | 1 | 4 |
| [upstream/emscripten-loading-progress](https://github.com/scummvm/scummvm/compare/master...chkuendig:scummvm:upstream/emscripten-loading-progress) | `upstream/master` | 1 | 1 | 2 |
| [upstream/cloud-streaming](https://github.com/chkuendig/scummvm/compare/7d736eeb9575105353c2841409e716bc5ae80372...upstream/cloud-streaming) | `upstream/emscripten-filesystem` | 3 | 7 | 23 |
| [upstream/hpl1-webgl](https://github.com/chkuendig/scummvm/compare/0f4e32c0aa5e2e09e6f13e08ba19c79b63ea176f...upstream/hpl1-webgl) | `upstream/emscripten-opengl` | 5 | 9 | 60 |
| [upstream/emscripten-recorder](https://github.com/scummvm/scummvm/compare/master...chkuendig:scummvm:upstream/emscripten-recorder) | `upstream/master` | 3 | 3 | 12 |
| [upstream/touch-controls](https://github.com/scummvm/scummvm/compare/master...chkuendig:scummvm:upstream/touch-controls) | `upstream/master` | 3 | 3 | 76 |

Suggested review order: library/core cleanup first, OpenGL next, then loading progress. Printing, filesystem/networking, recorder and touch controls can be reviewed independently in parallel. With SDK 6.0.13, apply cleanup’s port-library filtering when checking ImGui discovery; the rendering branch itself remains based on master.

Loading progress now changes only `custom_shell-pre.js` and `custom_shell.html`. It retains upstream MIDI initialization and does not inherit the SDK, JavaScript extraction or URL-reload work. Filesystem, printing and recorder likewise retain upstream inline backend APIs so their branches stand alone. Combining them with the later extraction commits needs ordinary conflict resolution; the demo already contains that integration.

The filesystem series has four commits: HTTP streaming/cache, dropped-file and Roland ROM import, persistent storage, and excluding HTTP waits from recorder timing. Recorder has three independent commits and guards HTTP timer integration with `USE_HTTP`. Cloud has three commits above filesystem. HPL1 has five above the complete four-commit OpenGL series; its shared engine-axis support also appears in touch controls and should be omitted during rebase once that API lands upstream.

Commit messages use short subjects and explanations only where they add useful context. Every review commit has one combined `Assisted-by` trailer and Christian as sole author and committer. The audit restored lost historical Claude credits, normalizing `Opus-5.5` to `claude-opus-5-5` while retaining other recorded model names. Detailed provenance is archived in the manifest.

The consolidated demo source is `e06972c3b9dbf756af23ebdaf3e08670fd8611d8`. All 32 review commits were cherry-picked with source markers, and all nine branch heads are ancestors. The independent-branch integration added two optional-HTTP guards in `gui/EventRecorder.cpp`. The latest rebase adds exactly the two new upstream commits; demo-specific changes are retained.

Validation: all review commit and branch whitespace checks pass, as do 18 unique shell/JavaScript/HTML syntax inputs, 28 standalone SDK 6.0.13 C++ syntax checks, six additional cloud C++ checks and two recorder preprocessor checks with HTTP on/off. Loading behavior tests cover known/unknown/compressed download sizes, initialization progress, response preservation, ordinary fetches, MIDI initialization and URL arguments. These are focused checks, not full standalone builds. No new browser run, full build or deployment was performed; earlier formatter findings are not all resolved.

The [last successful deployment](https://github.com/chkuendig/scummvm-demo/actions/runs/39470229200) remains SDK 6.0.13, demo `c8aa6ef69bc7266b21c27bbb305d9dd7c4032c92`, source `9e52e845659e3ec37112c5ae37cd52a2aaa44aa3`. Safari/iOS and physical-device feel were not tested in this refresh.

The removed Asyncify test/tooling and generated-JavaScript audio patches remain absent. The libmad `-fforce-mem` compatibility patch and original liba52 URL remain. Upstream memory flags and exported runtime helpers are retained. The monolithic runtime and URL-reload branches remain retired. No upstream PRs have been opened.

See the [commit list](upstream-pr-commits.md), [manifest and historical validation](upstream-pr-branches.json), and [SDK upgrade record](emscripten-6.0.13-upgrade.md).

On 2026-10-21 all nine series were rebased onto upstream `964f9ed828fc8538def571ca25b33d6dfbca1bbc` and all 32 commits reintegrated. Feature patches and messages are identical; the demo gains exactly the two new upstream commits. A fresh full SDK 6.0.13 build and deployment is requested for this revision.

The [fresh full build and deployment](https://github.com/chkuendig/scummvm-demo/actions/runs/39507150146) targets demo `d3879dcd2e9062ba952e37f5652963d73e6480f2` and source `e06972c3b9dbf756af23ebdaf3e08670fd8611d8`. At this record it is queued for GitHub-hosted runners; the last successful deployment remains unchanged.
