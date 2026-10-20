# Upstream review commits

There are 27 commits across nine review series, rebased onto upstream `ed949213a23440447ea402e263daa871394b6bf9`. Counts exclude each listed review base. Every review series has at most five commits and every complete stack at most ten.

## upstream/emscripten-update-cleanup

Review base: `upstream/master` (`ed949213a23`). 4 review commits, 4 including prerequisites.

- [b9a73fb3c76](https://github.com/chkuendig/scummvm/commit/b9a73fb3c760209215cec616c6aaf141b349f57a) EMSCRIPTEN: Extract WebMIDI into a JavaScript library
- [50cd93b54b9](https://github.com/chkuendig/scummvm/commit/50cd93b54b9a52345d4b55111480075f27dd6280) EMSCRIPTEN: Extract text-to-speech into a JavaScript library
- [d9ed2610ee8](https://github.com/chkuendig/scummvm/commit/d9ed2610ee8bf0891ab45d62a446d9f54dc6110f) EMSCRIPTEN: Extract browser backend APIs into a JavaScript library
- [c569c52908c](https://github.com/chkuendig/scummvm/commit/c569c52908c612c620c7e966b992091e4981babb) EMSCRIPTEN: Update to SDK 6.0.13 and refresh dependencies

## upstream/emscripten-opengl

Review base: `upstream/master` (`ed949213a23`). 4 review commits, 4 including prerequisites.

- [b7e92acd643](https://github.com/chkuendig/scummvm/commit/b7e92acd6435dce9077b0c53a3ff037f7a02f424) EMSCRIPTEN: Keep the WebGL canvas background opaque
- [b08ca402fa8](https://github.com/chkuendig/scummvm/commit/b08ca402fa8049e0d28d7fb76ea7152b403d7ad1) EMSCRIPTEN: Fall back to SurfaceSDL when WebGL is unavailable
- [29277836843](https://github.com/chkuendig/scummvm/commit/292778368430b9da364135b78a864e5619f7116d) EMSCRIPTEN: Match OpenGL video modes to browser window dimensions
- [7585c61a656](https://github.com/chkuendig/scummvm/commit/7585c61a6564ac280bf6b1e49ba40e6accb1de4c) EMSCRIPTEN: Use OpenGL ES 3 and WebGL2 by default

## upstream/emscripten-filesystem

Review base: `upstream/emscripten-update-cleanup` (`c569c52908c`). 3 review commits, 7 including prerequisites.

- [24539766ae3](https://github.com/chkuendig/scummvm/commit/24539766ae36ff99bee5dfe05e3cbe97458c2350) EMSCRIPTEN: Stream HTTP files through a bounded virtual filesystem
- [93a93efabcb](https://github.com/chkuendig/scummvm/commit/93a93efabcb411259e9d052d7dd7a3356b0be99a) EMSCRIPTEN: Mount dropped files and import Roland ROMs
- [e91b0eeb30a](https://github.com/chkuendig/scummvm/commit/e91b0eeb30a244643e1da935c32fd32d125a5d24) EMSCRIPTEN: Persist settings storage and use supported FS APIs

## upstream/emscripten-printing

Review base: `upstream/emscripten-update-cleanup` (`c569c52908c`). 1 review commit, 5 including prerequisites.

- [6cb3af3d8a8](https://github.com/chkuendig/scummvm/commit/6cb3af3d8a853732374a16306bafbc53cfbdd3a5) EMSCRIPTEN: Download game print-outs through the browser

## upstream/emscripten-loading-progress

Review base: `upstream/emscripten-update-cleanup` (`c569c52908c`). 1 review commit, 5 including prerequisites.

- [5d74baad5e1](https://github.com/chkuendig/scummvm/commit/5d74baad5e175f956db33db8ee513392738a1a85) EMSCRIPTEN: Show download and initialization progress

## upstream/cloud-streaming

Review base: `upstream/emscripten-filesystem` (`e91b0eeb30a`). 3 review commits, 10 including prerequisites.

- [938c562299e](https://github.com/chkuendig/scummvm/commit/938c562299ea64c017ada3a728b82616e16876bb) CLOUD: Support efficient ranged downloads
- [6ad0ef3c46b](https://github.com/chkuendig/scummvm/commit/6ad0ef3c46b59c9ef9e7f509f69cbc0adeeaa17c) CLOUD: Handle access tokens and browser refresh failures
- [5e641b2e4d0](https://github.com/chkuendig/scummvm/commit/5e641b2e4d01093309b8b76239ea0889a90bca8a) EMSCRIPTEN: Stream cloud files through the shared filesystem

## upstream/hpl1-webgl

Review base: `upstream/emscripten-opengl` (`c83ccc32509`). 5 review commits, 9 including prerequisites.

- [053650f01d2](https://github.com/chkuendig/scummvm/commit/053650f01d23d625d2c4becd3bed63fe6c2b117f) HPL1: Bundle shaders and adapt them for GLES
- [74c6f88283c](https://github.com/chkuendig/scummvm/commit/74c6f88283ce0ba62522e473efced9f0553a3c62) HPL1: Add the WebGL2 renderer and GLES compatibility layer
- [00787fad924](https://github.com/chkuendig/scummvm/commit/00787fad92414cf6aad1410b906602c20f8ea365) HPL1: Add controller bindings and menu focus navigation
- [247a7370958](https://github.com/chkuendig/scummvm/commit/247a73709587a63b22eee9723f433d9b6bbcd2d5) KEYMAPPER: Provide shared engine-axis actions for HPL1
- [57c02d3df44](https://github.com/chkuendig/scummvm/commit/57c02d3df44fc779ab52f8ca2925c26e07820b3a) HPL1: Handle native camera axes and preserve touch response

## upstream/emscripten-recorder

Review base: `upstream/emscripten-filesystem` (`e91b0eeb30a`). 3 review commits, 10 including prerequisites.

- [4777621a179](https://github.com/chkuendig/scummvm/commit/4777621a1795a4d41450343680d465c483fc6f77) COMMON: Propagate finalize() through buffered and recorder write streams
- [6299941f524](https://github.com/chkuendig/scummvm/commit/6299941f524ccd8080d864e97c4135d7040559a5) BACKENDS: EMSCRIPTEN: Support browser recording, replay and viewport controls
- [1c518f34be5](https://github.com/chkuendig/scummvm/commit/1c518f34be5990b6689cbecc8857901da065a8e6) BACKENDS: EMSCRIPTEN: Keep the SDL audio callback out of the event recorder

## upstream/touch-controls

Review base: `upstream/master` (`ed949213a23`). 3 review commits, 3 including prerequisites.

- [ebd7fe8c6db](https://github.com/chkuendig/scummvm/commit/ebd7fe8c6db2dc2077d67d86cb47736d43dbed3d) BACKENDS: Add shared on-screen controls and touch preferences
- [63f6fabc919](https://github.com/chkuendig/scummvm/commit/63f6fabc919d178890a30184888bc9f054a7a3f1) BACKENDS: Harmonize controller availability and touch switching
- [052dd2269c3](https://github.com/chkuendig/scummvm/commit/052dd2269c345b1dda12132613b500df6621aa17) BACKENDS: Emit touch joystick axes with the established response
