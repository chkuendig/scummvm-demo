# Upstream review commits

There are 27 commits across nine review series, rebased onto upstream `ed949213a23440447ea402e263daa871394b6bf9`. Counts exclude each listed review base. Every review series has at most five commits and every complete stack at most ten.

## upstream/emscripten-update-cleanup

Review base: `upstream/master` (`ed949213a23`). 4 review commits, 4 including prerequisites.

- [b9a73fb3c76](https://github.com/chkuendig/scummvm/commit/b9a73fb3c760209215cec616c6aaf141b349f57a) EMSCRIPTEN: Extract WebMIDI into a JavaScript library
- [50cd93b54b9](https://github.com/chkuendig/scummvm/commit/50cd93b54b9a52345d4b55111480075f27dd6280) EMSCRIPTEN: Extract text-to-speech into a JavaScript library
- [d9ed2610ee8](https://github.com/chkuendig/scummvm/commit/d9ed2610ee8bf0891ab45d62a446d9f54dc6110f) EMSCRIPTEN: Extract browser backend APIs into a JavaScript library
- [713b28eec47](https://github.com/chkuendig/scummvm/commit/713b28eec4770706a8071a158805ff2c784e23bd) EMSCRIPTEN: Update to SDK 6.0.13 and refresh dependencies

## upstream/emscripten-opengl

Review base: `upstream/master` (`ed949213a23`). 4 review commits, 4 including prerequisites.

- [b7e92acd643](https://github.com/chkuendig/scummvm/commit/b7e92acd6435dce9077b0c53a3ff037f7a02f424) EMSCRIPTEN: Keep the WebGL canvas background opaque
- [7da7123fe04](https://github.com/chkuendig/scummvm/commit/7da7123fe0487fddb815bf9f240c3738ef7f01cb) EMSCRIPTEN: Fall back to SurfaceSDL when WebGL is unavailable
- [90619d004b3](https://github.com/chkuendig/scummvm/commit/90619d004b3087d1bbaf4044aab7c7830c35397e) EMSCRIPTEN: Match OpenGL video modes to browser window dimensions
- [929e13b40b3](https://github.com/chkuendig/scummvm/commit/929e13b40b3e067650ceac237f39f4f2a46a640d) EMSCRIPTEN: Use OpenGL ES 3 and WebGL2 by default

## upstream/emscripten-filesystem

Review base: `upstream/emscripten-update-cleanup` (`c569c52908c`). 3 review commits, 7 including prerequisites.

- [61124a6e9ad](https://github.com/chkuendig/scummvm/commit/61124a6e9addf6adc5ec35b6d6df7009a80ddb34) EMSCRIPTEN: Stream HTTP files through a bounded virtual filesystem
- [f2e1f4072ad](https://github.com/chkuendig/scummvm/commit/f2e1f4072adb2dd1411faf82d29f1c1eab03e850) EMSCRIPTEN: Mount dropped files and import Roland ROMs
- [c845783aaca](https://github.com/chkuendig/scummvm/commit/c845783aaca27eb9463051b795e6af7f8660d8c2) EMSCRIPTEN: Persist settings storage and use supported FS APIs

## upstream/emscripten-printing

Review base: `upstream/emscripten-update-cleanup` (`c569c52908c`). 1 review commit, 5 including prerequisites.

- [09130305312](https://github.com/chkuendig/scummvm/commit/0913030531271f9cdab6b59aff967ec3488b5082) EMSCRIPTEN: Download game print-outs through the browser

## upstream/emscripten-loading-progress

Review base: `upstream/emscripten-update-cleanup` (`c569c52908c`). 1 review commit, 5 including prerequisites.

- [b85af9c0432](https://github.com/chkuendig/scummvm/commit/b85af9c04329a14fd752f0d82c5b4c27e19cbc59) EMSCRIPTEN: Show download and initialization progress

## upstream/cloud-streaming

Review base: `upstream/emscripten-filesystem` (`e91b0eeb30a`). 3 review commits, 10 including prerequisites.

- [db22562b6f4](https://github.com/chkuendig/scummvm/commit/db22562b6f4674d6815d49ed53bbdfd544856692) CLOUD: Support efficient ranged downloads
- [86af4ed0cb7](https://github.com/chkuendig/scummvm/commit/86af4ed0cb7b16bc9362ef688dc1b64f62ca328f) CLOUD: Handle access tokens and browser refresh failures
- [78b3d81b619](https://github.com/chkuendig/scummvm/commit/78b3d81b61918facf723ede02421e882bfeca477) EMSCRIPTEN: Stream cloud files through the shared filesystem

## upstream/hpl1-webgl

Review base: `upstream/emscripten-opengl` (`c83ccc32509`). 5 review commits, 9 including prerequisites.

- [2c61490ce40](https://github.com/chkuendig/scummvm/commit/2c61490ce40564880ecb132458e5f75986930ead) HPL1: Bundle shaders and adapt them for GLES
- [a0563685762](https://github.com/chkuendig/scummvm/commit/a05636857627fba406d6d60656b45c0eba3b04d4) HPL1: Add the WebGL2 renderer and GLES compatibility layer
- [ba95cb63169](https://github.com/chkuendig/scummvm/commit/ba95cb6316952387e4b6ba3467c81a1434a58891) HPL1: Add controller bindings and menu focus navigation
- [68c39ca6e26](https://github.com/chkuendig/scummvm/commit/68c39ca6e267b901c1db26c06640223dc4b1ba24) KEYMAPPER: Provide shared engine-axis actions for HPL1
- [e7760ed02cd](https://github.com/chkuendig/scummvm/commit/e7760ed02cd01bdbf6413acb09a58ab220b6149a) HPL1: Handle native camera axes and preserve touch response

## upstream/emscripten-recorder

Review base: `upstream/emscripten-filesystem` (`e91b0eeb30a`). 3 review commits, 10 including prerequisites.

- [b31cdac86c9](https://github.com/chkuendig/scummvm/commit/b31cdac86c966eda3266a9821f94fbce5c5720db) COMMON: Propagate finalize() through buffered and recorder write streams
- [89f9819016f](https://github.com/chkuendig/scummvm/commit/89f9819016fde97e1396e766af80a65ade254cca) BACKENDS: EMSCRIPTEN: Support browser recording, replay and viewport controls
- [55b404048c9](https://github.com/chkuendig/scummvm/commit/55b404048c942f637ac4d1e3e6f3c490b17cf9f5) BACKENDS: EMSCRIPTEN: Keep the SDL audio callback out of the event recorder

## upstream/touch-controls

Review base: `upstream/master` (`ed949213a23`). 3 review commits, 3 including prerequisites.

- [5299812069d](https://github.com/chkuendig/scummvm/commit/5299812069d678710c725a3d1144d73f9fbaec79) BACKENDS: Add shared on-screen controls and touch preferences
- [b3b5ce5e352](https://github.com/chkuendig/scummvm/commit/b3b5ce5e35279d79dd77a1ae927a32b327d230a7) BACKENDS: Harmonize controller availability and touch switching
- [d3ad51ee5f8](https://github.com/chkuendig/scummvm/commit/d3ad51ee5f868ffa826967301055ec5d665d1217) BACKENDS: Emit touch joystick axes with the established response
