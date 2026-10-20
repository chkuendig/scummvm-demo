# Upstream review commits

There are 27 commits across nine review series, rebased onto upstream `ed949213a23440447ea402e263daa871394b6bf9`. Counts exclude each listed review base. Every review series has at most five commits and every complete stack at most ten.

## upstream/emscripten-update-cleanup

Review base: `upstream/master` (`ed949213a23`). 4 review commits, 4 including prerequisites.

- [b9a73fb3c76](https://github.com/chkuendig/scummvm/commit/b9a73fb3c760209215cec616c6aaf141b349f57a) EMSCRIPTEN: Extract WebMIDI into a JavaScript library
- [50cd93b54b9](https://github.com/chkuendig/scummvm/commit/50cd93b54b9a52345d4b55111480075f27dd6280) EMSCRIPTEN: Extract text-to-speech into a JavaScript library
- [d9ed2610ee8](https://github.com/chkuendig/scummvm/commit/d9ed2610ee8bf0891ab45d62a446d9f54dc6110f) EMSCRIPTEN: Extract browser backend APIs into a JavaScript library
- [4968b30962b](https://github.com/chkuendig/scummvm/commit/4968b30962b603e73a3bcc277d3c87ec93029aae) EMSCRIPTEN: Update to SDK 6.0.13 and refresh dependencies

## upstream/emscripten-opengl

Review base: `upstream/master` (`ed949213a23`). 4 review commits, 4 including prerequisites.

- [b7e92acd643](https://github.com/chkuendig/scummvm/commit/b7e92acd6435dce9077b0c53a3ff037f7a02f424) EMSCRIPTEN: Keep the WebGL canvas background opaque
- [5ee92ede633](https://github.com/chkuendig/scummvm/commit/5ee92ede6336c4049f703f0d114bdd5ddedb00cf) EMSCRIPTEN: Fall back to SurfaceSDL when WebGL is unavailable
- [18e198169c5](https://github.com/chkuendig/scummvm/commit/18e198169c573909962665836a92dd1b1e5acc46) EMSCRIPTEN: Match OpenGL video modes to browser window dimensions
- [d003357706b](https://github.com/chkuendig/scummvm/commit/d003357706b8b596ae66604e97e29c10c8a1f3a4) EMSCRIPTEN: Use OpenGL ES 3 and WebGL2 by default

## upstream/emscripten-filesystem

Review base: `upstream/emscripten-update-cleanup` (`4968b30962b`). 3 review commits, 7 including prerequisites.

- [fb455e28ef8](https://github.com/chkuendig/scummvm/commit/fb455e28ef85c76d8b4e35f285236a47c8a05800) EMSCRIPTEN: Stream HTTP files through a bounded virtual filesystem
- [59a0d6a2d7d](https://github.com/chkuendig/scummvm/commit/59a0d6a2d7d76300a64f38bd3e35298b91a7606e) EMSCRIPTEN: Mount dropped files and import Roland ROMs
- [bcd09c38b74](https://github.com/chkuendig/scummvm/commit/bcd09c38b7492f5f9ead7188f4987790bc8e0f9a) EMSCRIPTEN: Persist settings storage and use supported FS APIs

## upstream/emscripten-printing

Review base: `upstream/emscripten-update-cleanup` (`4968b30962b`). 1 review commit, 5 including prerequisites.

- [45b99081b33](https://github.com/chkuendig/scummvm/commit/45b99081b333223f8fcb66fc39f41bbada3b718c) EMSCRIPTEN: Download game print-outs through the browser

## upstream/emscripten-loading-progress

Review base: `upstream/emscripten-update-cleanup` (`4968b30962b`). 1 review commit, 5 including prerequisites.

- [b94cd468d3a](https://github.com/chkuendig/scummvm/commit/b94cd468d3a9cba88ce32ad02b824fcd8f43fd50) EMSCRIPTEN: Show download and initialization progress

## upstream/cloud-streaming

Review base: `upstream/emscripten-filesystem` (`bcd09c38b74`). 3 review commits, 10 including prerequisites.

- [97969e53dee](https://github.com/chkuendig/scummvm/commit/97969e53deee6886dbb77729a9ea0bb1ce856f25) CLOUD: Support efficient ranged downloads
- [654a17f616b](https://github.com/chkuendig/scummvm/commit/654a17f616b7687e18e652e0a1bb15e568b911d1) CLOUD: Handle access tokens and browser refresh failures
- [5ecdf1c77e2](https://github.com/chkuendig/scummvm/commit/5ecdf1c77e2da4aa19efe68df8403cecc27918b1) EMSCRIPTEN: Stream cloud files through the shared filesystem

## upstream/hpl1-webgl

Review base: `upstream/emscripten-opengl` (`d003357706b`). 5 review commits, 9 including prerequisites.

- [8ca5d51e444](https://github.com/chkuendig/scummvm/commit/8ca5d51e4441f20f1d24eaf6e5a30fa551eb8aa9) HPL1: Bundle shaders and adapt them for GLES
- [e381df261fa](https://github.com/chkuendig/scummvm/commit/e381df261fa87e09bb9e63eb7aab0132f87b54f9) HPL1: Add the WebGL2 renderer and GLES compatibility layer
- [9c965fc9d6e](https://github.com/chkuendig/scummvm/commit/9c965fc9d6e03f2e42d89a0784437f33ac354bfa) HPL1: Add controller bindings and menu focus navigation
- [097aab1030f](https://github.com/chkuendig/scummvm/commit/097aab1030fd2c55aa1bffb94e3addee7de93348) KEYMAPPER: Provide shared engine-axis actions for HPL1
- [96cfc2faa16](https://github.com/chkuendig/scummvm/commit/96cfc2faa1651e8bdd96eb7e663a067721891c94) HPL1: Handle native camera axes and preserve touch response

## upstream/emscripten-recorder

Review base: `upstream/emscripten-filesystem` (`bcd09c38b74`). 3 review commits, 10 including prerequisites.

- [1e5c707959f](https://github.com/chkuendig/scummvm/commit/1e5c707959fbdca4c1edf896849b076a56086549) COMMON: Propagate finalize() through buffered and recorder write streams
- [14c78382f93](https://github.com/chkuendig/scummvm/commit/14c78382f937d791713bde81394398b24934a0a7) BACKENDS: EMSCRIPTEN: Support browser recording, replay and viewport controls
- [0d0fa8e1a38](https://github.com/chkuendig/scummvm/commit/0d0fa8e1a383cb76466b566e67ec8a71c0bb21d8) BACKENDS: EMSCRIPTEN: Keep the SDL audio callback out of the event recorder

## upstream/touch-controls

Review base: `upstream/master` (`ed949213a23`). 3 review commits, 3 including prerequisites.

- [ebd7fe8c6db](https://github.com/chkuendig/scummvm/commit/ebd7fe8c6db2dc2077d67d86cb47736d43dbed3d) BACKENDS: Add shared on-screen controls and touch preferences
- [63f6fabc919](https://github.com/chkuendig/scummvm/commit/63f6fabc919d178890a30184888bc9f054a7a3f1) BACKENDS: Harmonize controller availability and touch switching
- [052dd2269c3](https://github.com/chkuendig/scummvm/commit/052dd2269c345b1dda12132613b500df6621aa17) BACKENDS: Emit touch joystick axes with the established response
