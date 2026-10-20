# ScummVM review commits

Upstream base: `964f9ed828fc8538def571ca25b33d6dfbca1bbc`. 32 unique commits across nine review series; the limit excludes prerequisite commits. Seven series start on master. Cloud and HPL1 remain deferred stacks.

## upstream/emscripten-update-cleanup

Review base: `upstream/master` (`964f9ed828f`). 8 own commit(s), 8 including prerequisites.

- [8519e4111fd](https://github.com/chkuendig/scummvm/commit/8519e4111fd5f79355e6a89bc020e76e1a4c584f) EMSCRIPTEN: Extract WebMIDI into a JavaScript library
- [8c12c27ffd3](https://github.com/chkuendig/scummvm/commit/8c12c27ffd3574b1207f2b0138e4a592dd6058ad) EMSCRIPTEN: Extract text-to-speech into a JavaScript library
- [40475452d98](https://github.com/chkuendig/scummvm/commit/40475452d98007b9a04ff97074275a0fb2f52059) EMSCRIPTEN: Extract backend APIs into a JavaScript library
- [8c72a933e60](https://github.com/chkuendig/scummvm/commit/8c72a933e601986a3d6c6f84cdab2fe7d8f22c30) EMSCRIPTEN: Enable the browser virtual keyboard by default
- [ad832e50133](https://github.com/chkuendig/scummvm/commit/ad832e50133039cdf31231a0db084f15342255f4) EMSCRIPTEN: Guard SIGINT delivery on page unload
- [cd726413e11](https://github.com/chkuendig/scummvm/commit/cd726413e11e6f33375bc07f5b47426542f3cd1a) EMSCRIPTEN: Update Emscripten, RetroWave and libtheora
- [72e36afe9f9](https://github.com/chkuendig/scummvm/commit/72e36afe9f93c23247a11d474ea4480389699a67) EMSCRIPTEN: Filter native linker flags for port libraries
- [9280b781823](https://github.com/chkuendig/scummvm/commit/9280b78182332fb9ec4bc0ed56e2a7b4e032c7e9) EMSCRIPTEN: Include large engine data in distributions

## upstream/emscripten-opengl

Review base: `upstream/master` (`964f9ed828f`). 4 own commit(s), 4 including prerequisites.

- [df47fec23e7](https://github.com/chkuendig/scummvm/commit/df47fec23e727bcbfe8a859cb67c513e46374a27) EMSCRIPTEN: Keep the WebGL canvas background opaque
- [80cc2885c0d](https://github.com/chkuendig/scummvm/commit/80cc2885c0d9af90b1bf165c6d1605d34b409ccc) EMSCRIPTEN: Fall back to SurfaceSDL without WebGL
- [0394d583243](https://github.com/chkuendig/scummvm/commit/0394d583243dbc853cf0346d7445013ba23ee58c) EMSCRIPTEN: Size OpenGL modes to the browser window
- [0f4e32c0aa5](https://github.com/chkuendig/scummvm/commit/0f4e32c0aa5e2e09e6f13e08ba19c79b63ea176f) EMSCRIPTEN: Use OpenGL ES 3 and WebGL2 by default

## upstream/emscripten-filesystem

Review base: `upstream/master` (`964f9ed828f`). 4 own commit(s), 4 including prerequisites.

- [44fe95679b0](https://github.com/chkuendig/scummvm/commit/44fe95679b05708c5b987f679d4ecf25e5031cd1) EMSCRIPTEN: Stream HTTP files through a shared cache
- [9bed238b763](https://github.com/chkuendig/scummvm/commit/9bed238b76308e4abe73637416968fa15e6d2f74) EMSCRIPTEN: Mount dropped files and import Roland ROMs
- [8146695b7ad](https://github.com/chkuendig/scummvm/commit/8146695b7adec3b0f6bc8e9c969ce8b9d2f7fa90) EMSCRIPTEN: Request persistent storage for settings and saves
- [7d736eeb957](https://github.com/chkuendig/scummvm/commit/7d736eeb9575105353c2841409e716bc5ae80372) EMSCRIPTEN: Exclude HTTP waits from recorder timing

## upstream/emscripten-printing

Review base: `upstream/master` (`964f9ed828f`). 1 own commit(s), 1 including prerequisites.

- [be5c10388cb](https://github.com/chkuendig/scummvm/commit/be5c10388cb547ffdb0e468058e163431ed27ac3) EMSCRIPTEN: Download game printouts in the browser

## upstream/emscripten-loading-progress

Review base: `upstream/master` (`964f9ed828f`). 1 own commit(s), 1 including prerequisites.

- [e18bfabc7ee](https://github.com/chkuendig/scummvm/commit/e18bfabc7eec61057c94ad456533ab4e9c8d33cc) EMSCRIPTEN: Show download and initialization progress

## upstream/cloud-streaming

Review base: `upstream/emscripten-filesystem` (`7d736eeb957`). 3 own commit(s), 7 including prerequisites.

- [d3ddfb80b8d](https://github.com/chkuendig/scummvm/commit/d3ddfb80b8d5f6b012fec8cb077853e1a0f608f0) CLOUD: Add HTTP range downloads
- [9c832cac757](https://github.com/chkuendig/scummvm/commit/9c832cac7570d21f1f609a704c23a4a161d34f14) CLOUD: Handle token refresh failures in browsers
- [e3517dc3136](https://github.com/chkuendig/scummvm/commit/e3517dc3136779f035513e377086e79a723bb43d) EMSCRIPTEN: Use the shared cache for cloud files

## upstream/hpl1-webgl

Review base: `upstream/emscripten-opengl` (`0f4e32c0aa5`). 5 own commit(s), 9 including prerequisites.

- [28c35cd18b8](https://github.com/chkuendig/scummvm/commit/28c35cd18b8e1c714518d6751f9ffa145917a22e) HPL1: Bundle shaders and adapt them for GLES
- [9fddddbabc9](https://github.com/chkuendig/scummvm/commit/9fddddbabc92cd0d01d8faadc7b62a82a0d59850) HPL1: Add a GLES renderer for WebGL2
- [997e3909861](https://github.com/chkuendig/scummvm/commit/997e39098610c526524d6cd3598f3a4ad1f20321) HPL1: Add gamepad bindings and menu navigation
- [58ca3637b19](https://github.com/chkuendig/scummvm/commit/58ca3637b19fb0f80071b84dff045287abe1af6a) KEYMAPPER: Add engine joystick-axis actions
- [784f843f4d9](https://github.com/chkuendig/scummvm/commit/784f843f4d9029e54976c9d0ac8c148c8aa1e5ec) HPL1: Add gamepad camera controls

## upstream/emscripten-recorder

Review base: `upstream/master` (`964f9ed828f`). 3 own commit(s), 3 including prerequisites.

- [9e7fed2f62a](https://github.com/chkuendig/scummvm/commit/9e7fed2f62a474d204e46b508df7bb5309e8671e) COMMON: Finalize wrapped recorder streams
- [caf3b468cd1](https://github.com/chkuendig/scummvm/commit/caf3b468cd1505e62e001be6016c02c0b601d132) EMSCRIPTEN: Support recording and replay in the browser
- [3ebd51acd86](https://github.com/chkuendig/scummvm/commit/3ebd51acd865f0eb6ecc9e4b5088c886771a6858) EMSCRIPTEN: Avoid recorder callbacks in the audio mixer

## upstream/touch-controls

Review base: `upstream/master` (`964f9ed828f`). 3 own commit(s), 3 including prerequisites.

- [71245649ebe](https://github.com/chkuendig/scummvm/commit/71245649ebee2f675e943e815d02618b270197b6) BACKENDS: Add shared on-screen controls and touch settings
- [e666bea2506](https://github.com/chkuendig/scummvm/commit/e666bea25068f5616b75b9614e25b6f29aa3bddc) BACKENDS: Unify touch switching and controller detection
- [c56c0a92588](https://github.com/chkuendig/scummvm/commit/c56c0a92588ed5a203ec9cdea491ec21499a1f25) BACKENDS: Emit joystick axes from on-screen controls

All 32 are cherry-picked into demo `e06972c3b9dbf756af23ebdaf3e08670fd8611d8`. See the [branch overview](upstream-pr-branches.md) for review order and validation limits.

On 2026-10-21 all nine series were rebased onto upstream `964f9ed828fc8538def571ca25b33d6dfbca1bbc` and all 32 commits reintegrated. Feature patches and messages are identical; the demo gains exactly the two new upstream commits. A fresh full SDK 6.0.13 build and deployment is requested for this revision.
