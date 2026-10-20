# Upstream review commits

There are 24 commits across nine review series. Counts exclude the listed prerequisite branches; every series has at most five commits and every complete stack has at most ten. The SDK 6.0.13 bump is folded into the existing update/cleanup build commit.

## upstream/emscripten-update-cleanup

Review base: `upstream/master` (`71cb05b1c03`). 3 review commits, 3 including prerequisites.

- [acbbd71180e](https://github.com/chkuendig/scummvm/commit/acbbd71180e51fda1b1596b966fae92d953609d7) EMSCRIPTEN: Extract JavaScript APIs and tidy browser integration
- [4ac0d626b45](https://github.com/chkuendig/scummvm/commit/4ac0d626b45d02d5853137783c56b8aaad6498a2) EMSCRIPTEN: Update SDK, dependencies and Asyncify build handling
- [9d73527e327](https://github.com/chkuendig/scummvm/commit/9d73527e32736adfc321b3e1d860970e2298fd83) EMSCRIPTEN: Scope WebGL rendering fixes to the browser

## upstream/emscripten-filesystem

Review base: `upstream/emscripten-update-cleanup` (`9d73527e327`). 3 review commits, 6 including prerequisites.

- [9cb513573ca](https://github.com/chkuendig/scummvm/commit/9cb513573cabbc95b95be0e79270a4940fbac1cb) EMSCRIPTEN: Stream HTTP files through a bounded virtual filesystem
- [ef1843f6e30](https://github.com/chkuendig/scummvm/commit/ef1843f6e306e3875150f3c4e4f37f1939b580cb) EMSCRIPTEN: Mount dropped files and import Roland ROMs
- [afe98ff68ea](https://github.com/chkuendig/scummvm/commit/afe98ff68ea41ebdf7f0e8d09169fc1acda2e568) EMSCRIPTEN: Persist settings storage and use supported FS APIs

## upstream/emscripten-printing

Review base: `upstream/emscripten-update-cleanup` (`9d73527e327`). 1 review commit, 4 including prerequisites.

- [339a1327a67](https://github.com/chkuendig/scummvm/commit/339a1327a67279cbce3304c9a890b5ed3096cac3) EMSCRIPTEN: Download game print-outs through the browser

## upstream/emscripten-loading-progress

Review base: `upstream/emscripten-update-cleanup` (`9d73527e327`). 1 review commit, 4 including prerequisites.

- [977844ddba1](https://github.com/chkuendig/scummvm/commit/977844ddba15cc57ccb5553e7e2b4045f57d5953) EMSCRIPTEN: Show download and initialization progress

## upstream/emscripten-url-reload

Review base: `upstream/emscripten-update-cleanup` (`9d73527e327`). 1 review commit, 4 including prerequisites.

- [0226523707e](https://github.com/chkuendig/scummvm/commit/0226523707e04c143ac41f11a18434ce84e0c79f) EMSCRIPTEN: Reload when URL launch parameters change

## upstream/cloud-streaming

Review base: `upstream/emscripten-filesystem` (`afe98ff68ea`). 3 review commits, 9 including prerequisites.

- [9bfc118c5be](https://github.com/chkuendig/scummvm/commit/9bfc118c5bebfb874df6ac863f8f7c83c916780b) CLOUD: Support efficient ranged downloads
- [3ae6c2f7e45](https://github.com/chkuendig/scummvm/commit/3ae6c2f7e453cf2848169025c594620c3e7e6930) CLOUD: Handle access tokens and browser refresh failures
- [d044b36fbe0](https://github.com/chkuendig/scummvm/commit/d044b36fbe0183226852585781b21aa79bf30c62) EMSCRIPTEN: Stream cloud files through the shared filesystem

## upstream/hpl1-webgl

Review base: `upstream/emscripten-update-cleanup` (`9d73527e327`). 5 review commits, 8 including prerequisites.

- [e7479104466](https://github.com/chkuendig/scummvm/commit/e7479104466a5f1488372c22087df9a5b8b0c0b1) HPL1: Bundle shaders and adapt them for GLES
- [b54d6c79cc1](https://github.com/chkuendig/scummvm/commit/b54d6c79cc13155a0610baa9e9b78a2daf2ed2f5) HPL1: Add the WebGL2 renderer and GLES compatibility layer
- [1ccf72f65ab](https://github.com/chkuendig/scummvm/commit/1ccf72f65ab32a8abbd96fd6993cb78ef3a8b362) HPL1: Add controller bindings and menu focus navigation
- [6a0cc45eb5d](https://github.com/chkuendig/scummvm/commit/6a0cc45eb5ddb46702aabd4a1131589726135553) KEYMAPPER: Provide shared engine-axis actions for HPL1
- [275dfb8c481](https://github.com/chkuendig/scummvm/commit/275dfb8c481313cedae9dfaad2d2d7a928dc37c0) HPL1: Handle native camera axes and preserve touch response

## upstream/emscripten-recorder

Review base: `upstream/emscripten-filesystem` (`afe98ff68ea`). 4 review commits, 10 including prerequisites.

- [bc1c7f73e57](https://github.com/chkuendig/scummvm/commit/bc1c7f73e5776a933946d823c79b9efd32616dff) COMMON: Propagate finalize() through buffered and recorder write streams
- [6bb97b00256](https://github.com/chkuendig/scummvm/commit/6bb97b0025618d31391210eeb57e9c7800fde836) BACKENDS: EMSCRIPTEN: Make the event recorder work on the web port
- [b05d748b533](https://github.com/chkuendig/scummvm/commit/b05d748b533bc1ad100fc039107d093c77a49052) GUI: Fit web recorder controls to the letterboxed game area
- [a8e5e9c5d95](https://github.com/chkuendig/scummvm/commit/a8e5e9c5d95def785958563a972407d366b45fed) BACKENDS: EMSCRIPTEN: Keep the SDL audio callback out of the event recorder

## upstream/touch-controls

Review base: `upstream/master` (`71cb05b1c03`). 3 review commits, 3 including prerequisites.

- [192858a8587](https://github.com/chkuendig/scummvm/commit/192858a858733b4bb266fef43d06cb09871da60f) BACKENDS: Add shared on-screen controls and touch preferences
- [ab0a58104f0](https://github.com/chkuendig/scummvm/commit/ab0a58104f0a285e6cd5659e487ef49ec0933f54) BACKENDS: Harmonize controller availability and touch switching
- [8ef1023b2b8](https://github.com/chkuendig/scummvm/commit/8ef1023b2b8ee6413c44e76f1e3ca4abfbf54246) BACKENDS: Emit touch joystick axes with the established response
