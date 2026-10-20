# Emscripten 6.0.13 upgrade

SDK 6.0.13 is pinned in the source build script and demo workflow. The update includes SDL3 3.4.2, FreeType 2.14.3 and libpng 1.6.59; the combined dependency commit also updates libtheora to 1.2.0 and RetroWave to ddb5b34. Port-provided linker aliases and large engine-data packaging have separate cleanup commits. JavaScript extraction is split by library, with configure defaults and unload handling each separate.

The [6.0.13 release notes](https://github.com/emscripten-core/emscripten/releases/tag/6.0.13) record libpng 1.6.59 and removal of `FS.filesystems`. SDL3’s non-experimental status arrived in 6.0.10 and FreeType 2.14.3 in 6.0.7. The source uses supported FS APIs.

A clean local SDK smoke build previously linked SDL3, FreeType and libpng with Asyncify and ran under SDK Node 24.19.0. The [full validation build](https://github.com/chkuendig/scummvm-demo/actions/runs/39426597295) and [deployment](https://github.com/chkuendig/scummvm-demo/actions/runs/39470229200) passed for source `9e52e845659e3ec37112c5ae37cd52a2aaa44aa3`. That deployment remains live. Chromium launcher/HTTP browsing, Grim and Penumbra startup and touch smoke checks passed there; Safari/iOS and physical-device feel were not verified.

The latest review/demo integration is `e06972c3b9dbf756af23ebdaf3e08670fd8611d8`, based on upstream `964f9ed828fc8538def571ca25b33d6dfbca1bbc`. Seven branches now start directly on master. Cloud streaming stays on filesystem, and HPL1 on the full OpenGL series. Cleanup has eight commits, OpenGL four, filesystem four, printing one, loading one, cloud three, HPL1 five, recorder three and touch three. Limits exclude prerequisites. All 32 review commits were cherry-picked into the demo.

This refresh passed targeted shell/JS/HTML checks, 28 standalone C++ syntax checks with SDK 6.0.13, six additional cloud C++ checks, two optional-HTTP preprocessor checks, and Node VM tests of loading progress. It has not had a new full configure/build/link, browser run or deployment. The only change to the combined demo source is guarding recorder HTTP includes/timer calls when HTTP support is disabled.

Before deployment, run the full configured engine/plugin build using SDK-versioned caches, then exercise WebGL and SurfaceSDL fallback, HTTP ranges/cache, cloud authentication, drag/drop, persistent saves, loading, printing, recorder/replay and touch camera behavior. Use workflow dispatch with `deploy=false` for build-only validation. Rebuild all dependencies/plugins with the same SDK; do not mix SDK archives. Heavy host work must wait for the CI runner and use at most three jobs.

Generated-JavaScript audio patching and the obsolete Asyncify test/import tooling remain removed. Existing upstream Emscripten mixer/timer code remains active; recorder mixer timing uses `SDL_GetTicks()`. Earlier unpatched Chromium tests covered active audio and simulated blocked autoplay during HTTP browsing without errors; this does not establish physical iOS or full recorder behavior. The libmad compatibility patch and original liba52 archive URL remain at user request.

Configure retains upstream initial memory/stack settings, no explicit maximum, `_raise`, and runtime exports. The normal SDL3 ImGui capability check is preserved; Emscripten-only port-library filtering is in cleanup and should accompany SDK 6.0.13 rendering tests. Prior WebGL enabled/disabled browser validation used that fix. The formatter audit still has findings beyond corrected keyword spacing.

The [branch overview](upstream-pr-branches.md), [commit list](upstream-pr-commits.md), and [manifest](upstream-pr-branches.json) record current refs, assistance provenance and historical test results.

On 2026-10-21 all nine series were rebased onto upstream `964f9ed828fc8538def571ca25b33d6dfbca1bbc` and all 32 commits reintegrated. Feature patches and messages are identical; the demo gains exactly the two new upstream commits. A fresh full SDK 6.0.13 build and deployment is requested for this revision.
