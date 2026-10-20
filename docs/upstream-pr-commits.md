# Upstream review commits

There are 31 commits across nine review series, rebased onto upstream `ed949213a23440447ea402e263daa871394b6bf9`. The ten-commit limit applies to each review series above its listed base, excluding prerequisites. Cleanup has eight commits; the other series have at most five.

## upstream/emscripten-update-cleanup

Review base: `upstream/master` (`ed949213a23`). 8 review commits, 8 including prerequisites.

- [e4ec2302e10](https://github.com/chkuendig/scummvm/commit/e4ec2302e106e2c0d00a8226eb05823ab8953046) EMSCRIPTEN: Extract WebMIDI into a JavaScript library
- [949ebeb94b8](https://github.com/chkuendig/scummvm/commit/949ebeb94b8f56ff696bc0229d25b5787e8ed884) EMSCRIPTEN: Extract text-to-speech into a JavaScript library
- [8a920121b75](https://github.com/chkuendig/scummvm/commit/8a920121b754d4a1624ff9ebbf6bf0d407e86ad7) EMSCRIPTEN: Extract backend APIs into a JavaScript library
- [badafbbec50](https://github.com/chkuendig/scummvm/commit/badafbbec50cba92c86263b9ccfc08513655d55a) EMSCRIPTEN: Enable the browser virtual keyboard by default
- [b2feddd5f92](https://github.com/chkuendig/scummvm/commit/b2feddd5f9210b0141492caa2d3f307069c73d20) EMSCRIPTEN: Guard signal delivery on page unload
- [55ab3e7023b](https://github.com/chkuendig/scummvm/commit/55ab3e7023b18d0d445be8443bfac2fad43a0822) EMSCRIPTEN: Update Emscripten, RetroWave and libtheora
- [30457d55de4](https://github.com/chkuendig/scummvm/commit/30457d55de46a17d9561507e7f64e3cb8d05f080) EMSCRIPTEN: Filter linker aliases supplied by compiler ports
- [d9594d50608](https://github.com/chkuendig/scummvm/commit/d9594d50608288a36684f55dea65d153dac72201) EMSCRIPTEN: Include large engine data in distributions

## upstream/emscripten-opengl

Review base: `upstream/master` (`ed949213a23`). 4 review commits, 4 including prerequisites.

- [b7e92acd643](https://github.com/chkuendig/scummvm/commit/b7e92acd6435dce9077b0c53a3ff037f7a02f424) EMSCRIPTEN: Keep the WebGL canvas background opaque
- [7da7123fe04](https://github.com/chkuendig/scummvm/commit/7da7123fe0487fddb815bf9f240c3738ef7f01cb) EMSCRIPTEN: Fall back to SurfaceSDL when WebGL is unavailable
- [90619d004b3](https://github.com/chkuendig/scummvm/commit/90619d004b3087d1bbaf4044aab7c7830c35397e) EMSCRIPTEN: Match OpenGL video modes to browser window dimensions
- [929e13b40b3](https://github.com/chkuendig/scummvm/commit/929e13b40b3e067650ceac237f39f4f2a46a640d) EMSCRIPTEN: Use OpenGL ES 3 and WebGL2 by default

## upstream/emscripten-filesystem

Review base: `upstream/emscripten-update-cleanup` (`d9594d50608`). 3 review commits, 11 including prerequisites.

- [ec38d2a4cfc](https://github.com/chkuendig/scummvm/commit/ec38d2a4cfc5fde387f5559806da5a441928d51b) EMSCRIPTEN: Stream HTTP files through a bounded virtual filesystem
- [61c1e38c570](https://github.com/chkuendig/scummvm/commit/61c1e38c57078ad1b1de9d599a89b5dde82a44b1) EMSCRIPTEN: Mount dropped files and import Roland ROMs
- [64a66d6231c](https://github.com/chkuendig/scummvm/commit/64a66d6231c8eca4b6eada5db383d638fed5a6b6) EMSCRIPTEN: Persist settings storage and use supported FS APIs

## upstream/emscripten-printing

Review base: `upstream/emscripten-update-cleanup` (`d9594d50608`). 1 review commit, 9 including prerequisites.

- [54ecbc138c6](https://github.com/chkuendig/scummvm/commit/54ecbc138c635edd9bb26acebd6391fee38fb258) EMSCRIPTEN: Download game print-outs through the browser

## upstream/emscripten-loading-progress

Review base: `upstream/emscripten-update-cleanup` (`d9594d50608`). 1 review commit, 9 including prerequisites.

- [edddf2de872](https://github.com/chkuendig/scummvm/commit/edddf2de8726c88979029ddfeb81f15f7b225371) EMSCRIPTEN: Show download and initialization progress

## upstream/cloud-streaming

Review base: `upstream/emscripten-filesystem` (`64a66d6231c`). 3 review commits, 14 including prerequisites.

- [e7eb81a8533](https://github.com/chkuendig/scummvm/commit/e7eb81a8533e2879acf363bd4f251231f603632b) CLOUD: Support efficient ranged downloads
- [941629afdf4](https://github.com/chkuendig/scummvm/commit/941629afdf4c2ee1afba35038713e4a55b9afde7) CLOUD: Handle access tokens and browser refresh failures
- [2d6d2f38ef1](https://github.com/chkuendig/scummvm/commit/2d6d2f38ef16ad137a569ba56c17036c734b0a05) EMSCRIPTEN: Stream cloud files through the shared filesystem

## upstream/hpl1-webgl

Review base: `upstream/emscripten-opengl` (`929e13b40b3`). 5 review commits, 9 including prerequisites.

- [2c61490ce40](https://github.com/chkuendig/scummvm/commit/2c61490ce40564880ecb132458e5f75986930ead) HPL1: Bundle shaders and adapt them for GLES
- [a0563685762](https://github.com/chkuendig/scummvm/commit/a05636857627fba406d6d60656b45c0eba3b04d4) HPL1: Add the WebGL2 renderer and GLES compatibility layer
- [ba95cb63169](https://github.com/chkuendig/scummvm/commit/ba95cb6316952387e4b6ba3467c81a1434a58891) HPL1: Add controller bindings and menu focus navigation
- [68c39ca6e26](https://github.com/chkuendig/scummvm/commit/68c39ca6e267b901c1db26c06640223dc4b1ba24) KEYMAPPER: Provide shared engine-axis actions for HPL1
- [e7760ed02cd](https://github.com/chkuendig/scummvm/commit/e7760ed02cd01bdbf6413acb09a58ab220b6149a) HPL1: Handle native camera axes and preserve touch response

## upstream/emscripten-recorder

Review base: `upstream/emscripten-filesystem` (`64a66d6231c`). 3 review commits, 14 including prerequisites.

- [e4b9e82606a](https://github.com/chkuendig/scummvm/commit/e4b9e82606a63d3b39330704a0b7390af2e018ca) COMMON: Propagate finalize() through buffered and recorder write streams
- [d9856d93c22](https://github.com/chkuendig/scummvm/commit/d9856d93c223563ed9d26c251583c7294b2f8dc6) BACKENDS: EMSCRIPTEN: Support browser recording, replay and viewport controls
- [5aa6a2a8597](https://github.com/chkuendig/scummvm/commit/5aa6a2a859734e5572b01f6779de07cfe7f81edc) BACKENDS: EMSCRIPTEN: Keep the SDL audio callback out of the event recorder

## upstream/touch-controls

Review base: `upstream/master` (`ed949213a23`). 3 review commits, 3 including prerequisites.

- [5299812069d](https://github.com/chkuendig/scummvm/commit/5299812069d678710c725a3d1144d73f9fbaec79) BACKENDS: Add shared on-screen controls and touch preferences
- [b3b5ce5e352](https://github.com/chkuendig/scummvm/commit/b3b5ce5e35279d79dd77a1ae927a32b327d230a7) BACKENDS: Harmonize controller availability and touch switching
- [d3ad51ee5f8](https://github.com/chkuendig/scummvm/commit/d3ad51ee5f868ffa826967301055ec5d665d1217) BACKENDS: Emit touch joystick axes with the established response
