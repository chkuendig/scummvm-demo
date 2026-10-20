# Upstream review commits

There are 30 commits across nine review series, rebased onto upstream `ed949213a23440447ea402e263daa871394b6bf9`. The ten-commit limit applies to each review series above its listed base, excluding prerequisites. Cleanup has seven commits; the other series have at most five.

## upstream/emscripten-update-cleanup

Review base: `upstream/master` (`ed949213a23`). 7 review commits, 7 including prerequisites.

- [b9a73fb3c76](https://github.com/chkuendig/scummvm/commit/b9a73fb3c760209215cec616c6aaf141b349f57a) EMSCRIPTEN: Extract WebMIDI into a JavaScript library
- [50cd93b54b9](https://github.com/chkuendig/scummvm/commit/50cd93b54b9a52345d4b55111480075f27dd6280) EMSCRIPTEN: Extract text-to-speech into a JavaScript library
- [52ad32a9712](https://github.com/chkuendig/scummvm/commit/52ad32a971296188859cb23ae1c415b99972c8e2) EMSCRIPTEN: Extract browser backend APIs into a JavaScript library
- [6b6fb53cb8b](https://github.com/chkuendig/scummvm/commit/6b6fb53cb8b513c650eeaa7c3534ef2618a5eae1) EMSCRIPTEN: Update to SDK 6.0.13
- [7c7d5d0d71e](https://github.com/chkuendig/scummvm/commit/7c7d5d0d71eba02e73679dca2975455b18bcf47b) EMSCRIPTEN: Update libtheora and RetroWave
- [6d2d864bcea](https://github.com/chkuendig/scummvm/commit/6d2d864bcea4eb1cf93a7a63a4d6c4285cfc85f9) EMSCRIPTEN: Filter linker aliases supplied by compiler ports
- [81a24b609a2](https://github.com/chkuendig/scummvm/commit/81a24b609a2dfaf495974f3e06309549cbad5bc5) EMSCRIPTEN: Include large engine data in distributions

## upstream/emscripten-opengl

Review base: `upstream/master` (`ed949213a23`). 4 review commits, 4 including prerequisites.

- [b7e92acd643](https://github.com/chkuendig/scummvm/commit/b7e92acd6435dce9077b0c53a3ff037f7a02f424) EMSCRIPTEN: Keep the WebGL canvas background opaque
- [7da7123fe04](https://github.com/chkuendig/scummvm/commit/7da7123fe0487fddb815bf9f240c3738ef7f01cb) EMSCRIPTEN: Fall back to SurfaceSDL when WebGL is unavailable
- [90619d004b3](https://github.com/chkuendig/scummvm/commit/90619d004b3087d1bbaf4044aab7c7830c35397e) EMSCRIPTEN: Match OpenGL video modes to browser window dimensions
- [929e13b40b3](https://github.com/chkuendig/scummvm/commit/929e13b40b3e067650ceac237f39f4f2a46a640d) EMSCRIPTEN: Use OpenGL ES 3 and WebGL2 by default

## upstream/emscripten-filesystem

Review base: `upstream/emscripten-update-cleanup` (`81a24b609a2`). 3 review commits, 10 including prerequisites.

- [18334538e75](https://github.com/chkuendig/scummvm/commit/18334538e750e3691d11cbcf246d0b6783408ea5) EMSCRIPTEN: Stream HTTP files through a bounded virtual filesystem
- [9584e111d37](https://github.com/chkuendig/scummvm/commit/9584e111d377d8f409a141da9d83c707dfedcc61) EMSCRIPTEN: Mount dropped files and import Roland ROMs
- [0f517a13bd9](https://github.com/chkuendig/scummvm/commit/0f517a13bd927dd27ee48159ab49478aed450e83) EMSCRIPTEN: Persist settings storage and use supported FS APIs

## upstream/emscripten-printing

Review base: `upstream/emscripten-update-cleanup` (`81a24b609a2`). 1 review commit, 8 including prerequisites.

- [4675b6a6f74](https://github.com/chkuendig/scummvm/commit/4675b6a6f748f215a2b6950ecc1436a0b3dcd7ff) EMSCRIPTEN: Download game print-outs through the browser

## upstream/emscripten-loading-progress

Review base: `upstream/emscripten-update-cleanup` (`81a24b609a2`). 1 review commit, 8 including prerequisites.

- [a592eee7cd8](https://github.com/chkuendig/scummvm/commit/a592eee7cd877066fc55bd54b8795bc76393b027) EMSCRIPTEN: Show download and initialization progress

## upstream/cloud-streaming

Review base: `upstream/emscripten-filesystem` (`0f517a13bd9`). 3 review commits, 13 including prerequisites.

- [fa051463bcb](https://github.com/chkuendig/scummvm/commit/fa051463bcb249b1ddb747e135a1ff7f298d7e30) CLOUD: Support efficient ranged downloads
- [96d0b5c28a0](https://github.com/chkuendig/scummvm/commit/96d0b5c28a04fd13c28b076e8f5dc6475a02696a) CLOUD: Handle access tokens and browser refresh failures
- [f20d2565e93](https://github.com/chkuendig/scummvm/commit/f20d2565e93b849fcf8f6a499dd4efa448b7a4d3) EMSCRIPTEN: Stream cloud files through the shared filesystem

## upstream/hpl1-webgl

Review base: `upstream/emscripten-opengl` (`929e13b40b3`). 5 review commits, 9 including prerequisites.

- [2c61490ce40](https://github.com/chkuendig/scummvm/commit/2c61490ce40564880ecb132458e5f75986930ead) HPL1: Bundle shaders and adapt them for GLES
- [a0563685762](https://github.com/chkuendig/scummvm/commit/a05636857627fba406d6d60656b45c0eba3b04d4) HPL1: Add the WebGL2 renderer and GLES compatibility layer
- [ba95cb63169](https://github.com/chkuendig/scummvm/commit/ba95cb6316952387e4b6ba3467c81a1434a58891) HPL1: Add controller bindings and menu focus navigation
- [68c39ca6e26](https://github.com/chkuendig/scummvm/commit/68c39ca6e267b901c1db26c06640223dc4b1ba24) KEYMAPPER: Provide shared engine-axis actions for HPL1
- [e7760ed02cd](https://github.com/chkuendig/scummvm/commit/e7760ed02cd01bdbf6413acb09a58ab220b6149a) HPL1: Handle native camera axes and preserve touch response

## upstream/emscripten-recorder

Review base: `upstream/emscripten-filesystem` (`0f517a13bd9`). 3 review commits, 13 including prerequisites.

- [3641f88987b](https://github.com/chkuendig/scummvm/commit/3641f88987b6cbda1b65f9dac3d1ecb9f691275b) COMMON: Propagate finalize() through buffered and recorder write streams
- [e7407cc0df3](https://github.com/chkuendig/scummvm/commit/e7407cc0df315fe7c5f73d054152d83684bbe7f7) BACKENDS: EMSCRIPTEN: Support browser recording, replay and viewport controls
- [e629259f839](https://github.com/chkuendig/scummvm/commit/e629259f8396f7e1495a2f36907d65ae7db5c8cf) BACKENDS: EMSCRIPTEN: Keep the SDL audio callback out of the event recorder

## upstream/touch-controls

Review base: `upstream/master` (`ed949213a23`). 3 review commits, 3 including prerequisites.

- [5299812069d](https://github.com/chkuendig/scummvm/commit/5299812069d678710c725a3d1144d73f9fbaec79) BACKENDS: Add shared on-screen controls and touch preferences
- [b3b5ce5e352](https://github.com/chkuendig/scummvm/commit/b3b5ce5e35279d79dd77a1ae927a32b327d230a7) BACKENDS: Harmonize controller availability and touch switching
- [d3ad51ee5f8](https://github.com/chkuendig/scummvm/commit/d3ad51ee5f868ffa826967301055ec5d665d1217) BACKENDS: Emit touch joystick axes with the established response
