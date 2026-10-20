# Upstream review commits

There are 24 commits across nine review series, rebased onto upstream `ed949213a23440447ea402e263daa871394b6bf9`. Counts exclude each listed review base. Every review series has at most five commits and every complete stack at most ten.

## upstream/emscripten-update-cleanup

Review base: `upstream/master` (`ed949213a23`). 4 review commits, 4 including prerequisites.

- [b9a73fb3c76](https://github.com/chkuendig/scummvm/commit/b9a73fb3c760209215cec616c6aaf141b349f57a) EMSCRIPTEN: Extract WebMIDI into a JavaScript library
- [50cd93b54b9](https://github.com/chkuendig/scummvm/commit/50cd93b54b9a52345d4b55111480075f27dd6280) EMSCRIPTEN: Extract text-to-speech into a JavaScript library
- [e30dbf5c112](https://github.com/chkuendig/scummvm/commit/e30dbf5c1125db4921ba5ff79a99bc6776c78539) EMSCRIPTEN: Extract browser backend APIs into a JavaScript library
- [3100d77b580](https://github.com/chkuendig/scummvm/commit/3100d77b5804f5bb765d7ddd36c76870555cc73b) EMSCRIPTEN: Update to SDK 6.0.13 and refresh dependencies

## upstream/emscripten-opengl

Review base: `upstream/emscripten-update-cleanup` (`3100d77b580`). 1 review commit, 5 including prerequisites.

- [a1302e4a723](https://github.com/chkuendig/scummvm/commit/a1302e4a7231d79d41a9b3af5fad9c9fa3608667) EMSCRIPTEN: Scope WebGL rendering fixes to the browser

## upstream/emscripten-filesystem

Review base: `upstream/emscripten-update-cleanup` (`3100d77b580`). 3 review commits, 7 including prerequisites.

- [ea5355b3f55](https://github.com/chkuendig/scummvm/commit/ea5355b3f55bb746bb031178c11f021c9e30e2ce) EMSCRIPTEN: Stream HTTP files through a bounded virtual filesystem
- [122c839299d](https://github.com/chkuendig/scummvm/commit/122c839299d2ca158a4554cd1e9a44051f08e50c) EMSCRIPTEN: Mount dropped files and import Roland ROMs
- [e71b030436a](https://github.com/chkuendig/scummvm/commit/e71b030436aa4ae77f7e984d0e058e12d0dc52c6) EMSCRIPTEN: Persist settings storage and use supported FS APIs

## upstream/emscripten-printing

Review base: `upstream/emscripten-update-cleanup` (`3100d77b580`). 1 review commit, 5 including prerequisites.

- [2a7fb40ccf4](https://github.com/chkuendig/scummvm/commit/2a7fb40ccf48707eef301174230c92bb7231b880) EMSCRIPTEN: Download game print-outs through the browser

## upstream/emscripten-loading-progress

Review base: `upstream/emscripten-update-cleanup` (`3100d77b580`). 1 review commit, 5 including prerequisites.

- [62f5898ead2](https://github.com/chkuendig/scummvm/commit/62f5898ead2a089d4178268b3bd4b8632d7c7d71) EMSCRIPTEN: Show download and initialization progress

## upstream/cloud-streaming

Review base: `upstream/emscripten-filesystem` (`e71b030436a`). 3 review commits, 10 including prerequisites.

- [45100e0408d](https://github.com/chkuendig/scummvm/commit/45100e0408d09abc8211fc968176973533929f58) CLOUD: Support efficient ranged downloads
- [4333adf305c](https://github.com/chkuendig/scummvm/commit/4333adf305cfd1d1ffd5d1a5ce703a2a9f14a74e) CLOUD: Handle access tokens and browser refresh failures
- [1583b35b0e6](https://github.com/chkuendig/scummvm/commit/1583b35b0e6230d3bfecf12b53c0048dfa4a079a) EMSCRIPTEN: Stream cloud files through the shared filesystem

## upstream/hpl1-webgl

Review base: `upstream/emscripten-opengl` (`a1302e4a723`). 5 review commits, 10 including prerequisites.

- [3fc2bfdd96b](https://github.com/chkuendig/scummvm/commit/3fc2bfdd96bd3e2d3a40b7736fbdae8ae4c34c15) HPL1: Bundle shaders and adapt them for GLES
- [525586c0afe](https://github.com/chkuendig/scummvm/commit/525586c0afe7dbf2adce5bb925acaf51e7740655) HPL1: Add the WebGL2 renderer and GLES compatibility layer
- [ad2fa65e17e](https://github.com/chkuendig/scummvm/commit/ad2fa65e17e00a48aafa7d1661231d0681d274e1) HPL1: Add controller bindings and menu focus navigation
- [bc864206e6e](https://github.com/chkuendig/scummvm/commit/bc864206e6e5d1fc116009db9a143c18ad5e9165) KEYMAPPER: Provide shared engine-axis actions for HPL1
- [7e6fd9711e5](https://github.com/chkuendig/scummvm/commit/7e6fd9711e5030c7924dd09a5715305dcca9f4c6) HPL1: Handle native camera axes and preserve touch response

## upstream/emscripten-recorder

Review base: `upstream/emscripten-filesystem` (`e71b030436a`). 3 review commits, 10 including prerequisites.

- [4cbf7631c8a](https://github.com/chkuendig/scummvm/commit/4cbf7631c8a4be65878a20c336676349f6ec8edb) COMMON: Propagate finalize() through buffered and recorder write streams
- [295676adccf](https://github.com/chkuendig/scummvm/commit/295676adccf39c470a3042fae5a619a890c48a25) BACKENDS: EMSCRIPTEN: Support browser recording, replay and viewport controls
- [f2e3883212c](https://github.com/chkuendig/scummvm/commit/f2e3883212ca9facbc2d36f2d389f5dec73c7687) BACKENDS: EMSCRIPTEN: Keep the SDL audio callback out of the event recorder

## upstream/touch-controls

Review base: `upstream/master` (`ed949213a23`). 3 review commits, 3 including prerequisites.

- [ebd7fe8c6db](https://github.com/chkuendig/scummvm/commit/ebd7fe8c6db2dc2077d67d86cb47736d43dbed3d) BACKENDS: Add shared on-screen controls and touch preferences
- [63f6fabc919](https://github.com/chkuendig/scummvm/commit/63f6fabc919d178890a30184888bc9f054a7a3f1) BACKENDS: Harmonize controller availability and touch switching
- [052dd2269c3](https://github.com/chkuendig/scummvm/commit/052dd2269c345b1dda12132613b500df6621aa17) BACKENDS: Emit touch joystick axes with the established response
