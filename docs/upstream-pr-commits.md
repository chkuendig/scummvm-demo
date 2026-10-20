# Upstream review commits

There are 24 commits across nine review series, rebased onto upstream `ed949213a23440447ea402e263daa871394b6bf9`. Counts exclude each listed review base. Every review series has at most five commits and every complete stack at most ten.

## upstream/emscripten-update-cleanup

Review base: `upstream/master` (`ed949213a23`). 4 review commits, 4 including prerequisites.

- [9f3b5a4a0a6](https://github.com/chkuendig/scummvm/commit/9f3b5a4a0a605e360dd3ef6edb849ecb080eed30) EMSCRIPTEN: Extract WebMIDI into a JavaScript library
- [bd2d003c92c](https://github.com/chkuendig/scummvm/commit/bd2d003c92c5061a6a47e73f9d846043556b52b5) EMSCRIPTEN: Extract text-to-speech into a JavaScript library
- [eb0b50b2575](https://github.com/chkuendig/scummvm/commit/eb0b50b25751c723033fee1da7453452c1e16b86) EMSCRIPTEN: Extract browser backend APIs into a JavaScript library
- [7a5be6a0974](https://github.com/chkuendig/scummvm/commit/7a5be6a0974f5ab063f0ee89b96fbd0a6222bb8e) EMSCRIPTEN: Update SDK, dependencies and Asyncify build handling

## upstream/emscripten-opengl

Review base: `upstream/emscripten-update-cleanup` (`7a5be6a0974`). 1 review commit, 5 including prerequisites.

- [5e488cb226c](https://github.com/chkuendig/scummvm/commit/5e488cb226c63f3b6daf6cfdad998c4e17b3a8fc) EMSCRIPTEN: Scope WebGL rendering fixes to the browser

## upstream/emscripten-filesystem

Review base: `upstream/emscripten-update-cleanup` (`7a5be6a0974`). 3 review commits, 7 including prerequisites.

- [3e5151be407](https://github.com/chkuendig/scummvm/commit/3e5151be4070a20fe46149150ada9fc7bc8ff8e5) EMSCRIPTEN: Stream HTTP files through a bounded virtual filesystem
- [acc49da32fb](https://github.com/chkuendig/scummvm/commit/acc49da32fb178fa78432293d98f90fe98f4226a) EMSCRIPTEN: Mount dropped files and import Roland ROMs
- [2d2e3cddf1d](https://github.com/chkuendig/scummvm/commit/2d2e3cddf1dca7ee567d564e3e2cb5ac5a59cfef) EMSCRIPTEN: Persist settings storage and use supported FS APIs

## upstream/emscripten-printing

Review base: `upstream/emscripten-update-cleanup` (`7a5be6a0974`). 1 review commit, 5 including prerequisites.

- [6341a7fa0fb](https://github.com/chkuendig/scummvm/commit/6341a7fa0fbd2726599be516e5518c160ddbf8a0) EMSCRIPTEN: Download game print-outs through the browser

## upstream/emscripten-loading-progress

Review base: `upstream/emscripten-update-cleanup` (`7a5be6a0974`). 1 review commit, 5 including prerequisites.

- [d35aab3551d](https://github.com/chkuendig/scummvm/commit/d35aab3551d55649439797af57b1687c92569cc4) EMSCRIPTEN: Show download and initialization progress

## upstream/cloud-streaming

Review base: `upstream/emscripten-filesystem` (`2d2e3cddf1d`). 3 review commits, 10 including prerequisites.

- [b3b340a446b](https://github.com/chkuendig/scummvm/commit/b3b340a446bd8b1293798be0e35d5cb7489b3573) CLOUD: Support efficient ranged downloads
- [4894b1d441a](https://github.com/chkuendig/scummvm/commit/4894b1d441a3c421c4a404b2330494e6a0297c08) CLOUD: Handle access tokens and browser refresh failures
- [31bd47dc122](https://github.com/chkuendig/scummvm/commit/31bd47dc122e3901cf0f1e0345933ae6308e075d) EMSCRIPTEN: Stream cloud files through the shared filesystem

## upstream/hpl1-webgl

Review base: `upstream/emscripten-opengl` (`5e488cb226c`). 5 review commits, 10 including prerequisites.

- [fb572df251d](https://github.com/chkuendig/scummvm/commit/fb572df251db3b39046eb3d83a4cb81f5b041075) HPL1: Bundle shaders and adapt them for GLES
- [5ae3a168623](https://github.com/chkuendig/scummvm/commit/5ae3a1686238c6c203fe0aa6b3bb4253842c833b) HPL1: Add the WebGL2 renderer and GLES compatibility layer
- [ebd040b2a20](https://github.com/chkuendig/scummvm/commit/ebd040b2a202404e0b3252606e585694cc1704be) HPL1: Add controller bindings and menu focus navigation
- [d294a87c65e](https://github.com/chkuendig/scummvm/commit/d294a87c65e7d034319bfb75f1eb361c61ac5bd9) KEYMAPPER: Provide shared engine-axis actions for HPL1
- [4f0b2897d23](https://github.com/chkuendig/scummvm/commit/4f0b2897d23292a4c28e9d441d6ef312a3ca7e42) HPL1: Handle native camera axes and preserve touch response

## upstream/emscripten-recorder

Review base: `upstream/emscripten-filesystem` (`2d2e3cddf1d`). 3 review commits, 10 including prerequisites.

- [574c581c1d7](https://github.com/chkuendig/scummvm/commit/574c581c1d7b7b68ecf5230397f9e1317b90bd72) COMMON: Propagate finalize() through buffered and recorder write streams
- [d493eb92a98](https://github.com/chkuendig/scummvm/commit/d493eb92a98c7f488e09356dc8c654e8a620088c) BACKENDS: EMSCRIPTEN: Support browser recording, replay and viewport controls
- [05f12c5d382](https://github.com/chkuendig/scummvm/commit/05f12c5d38265ed8d44a95c094b6a01e7646169e) BACKENDS: EMSCRIPTEN: Keep the SDL audio callback out of the event recorder

## upstream/touch-controls

Review base: `upstream/master` (`ed949213a23`). 3 review commits, 3 including prerequisites.

- [ebd7fe8c6db](https://github.com/chkuendig/scummvm/commit/ebd7fe8c6db2dc2077d67d86cb47736d43dbed3d) BACKENDS: Add shared on-screen controls and touch preferences
- [63f6fabc919](https://github.com/chkuendig/scummvm/commit/63f6fabc919d178890a30184888bc9f054a7a3f1) BACKENDS: Harmonize controller availability and touch switching
- [052dd2269c3](https://github.com/chkuendig/scummvm/commit/052dd2269c345b1dda12132613b500df6621aa17) BACKENDS: Emit touch joystick axes with the established response
