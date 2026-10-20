# ScummVM review commits

Upstream base: `ed949213a23440447ea402e263daa871394b6bf9`. 32 unique commits across nine review series; the limit excludes prerequisite commits. Seven series start on master. Cloud and HPL1 remain deferred stacks.

## upstream/emscripten-update-cleanup

Review base: `upstream/master` (`ed949213a23`). 8 own commit(s), 8 including prerequisites.

- [ea8dee1d2d2](https://github.com/chkuendig/scummvm/commit/ea8dee1d2d2eebb801eab13c34ac8ab41b5970ed) EMSCRIPTEN: Extract WebMIDI into a JavaScript library
- [463a04b046e](https://github.com/chkuendig/scummvm/commit/463a04b046eff7271556e54fffb884df6c4e72cb) EMSCRIPTEN: Extract text-to-speech into a JavaScript library
- [f8021132039](https://github.com/chkuendig/scummvm/commit/f8021132039b3fe437a35a10d6aacc0966ccc16b) EMSCRIPTEN: Extract backend APIs into a JavaScript library
- [75d11c34568](https://github.com/chkuendig/scummvm/commit/75d11c345681f3711bab055178a788e036ed9e3e) EMSCRIPTEN: Enable the browser virtual keyboard by default
- [e19663bba15](https://github.com/chkuendig/scummvm/commit/e19663bba15bd1e4e8097a8644e0e78f64097ea8) EMSCRIPTEN: Guard SIGINT delivery on page unload
- [0178d29e226](https://github.com/chkuendig/scummvm/commit/0178d29e2265c9afb2943a293f20e6fa1bfd64f8) EMSCRIPTEN: Update Emscripten, RetroWave and libtheora
- [cd9d7d14437](https://github.com/chkuendig/scummvm/commit/cd9d7d1443773e0610b478fdaa6f6e941382e79d) EMSCRIPTEN: Filter native linker flags for port libraries
- [8d951f90ff8](https://github.com/chkuendig/scummvm/commit/8d951f90ff89b2ca005cf4780c56e4e93d961f46) EMSCRIPTEN: Include large engine data in distributions

## upstream/emscripten-opengl

Review base: `upstream/master` (`ed949213a23`). 4 own commit(s), 4 including prerequisites.

- [b3d452dd738](https://github.com/chkuendig/scummvm/commit/b3d452dd73840976ec771e3f8eb4a5ab8b0c4378) EMSCRIPTEN: Keep the WebGL canvas background opaque
- [d151d605a35](https://github.com/chkuendig/scummvm/commit/d151d605a355559e3765cda7b72b89390b4c1776) EMSCRIPTEN: Fall back to SurfaceSDL without WebGL
- [16d8587a437](https://github.com/chkuendig/scummvm/commit/16d8587a4370a8ee5306314bfde22f66213a7f65) EMSCRIPTEN: Size OpenGL modes to the browser window
- [69031266a7f](https://github.com/chkuendig/scummvm/commit/69031266a7fe5867ae4e8fb8002d882a8b2d95de) EMSCRIPTEN: Use OpenGL ES 3 and WebGL2 by default

## upstream/emscripten-filesystem

Review base: `upstream/master` (`ed949213a23`). 4 own commit(s), 4 including prerequisites.

- [e0b6d2ec0cf](https://github.com/chkuendig/scummvm/commit/e0b6d2ec0cf85da20b5aa4d817e882d36843f861) EMSCRIPTEN: Stream HTTP files through a shared cache
- [a5757f51cb8](https://github.com/chkuendig/scummvm/commit/a5757f51cb84449c0c2c536b8b78aaf5f3424ffb) EMSCRIPTEN: Mount dropped files and import Roland ROMs
- [0bc3aa010a1](https://github.com/chkuendig/scummvm/commit/0bc3aa010a186e5dbdab69096371a71def4cbe0d) EMSCRIPTEN: Request persistent storage for settings and saves
- [a55376a4974](https://github.com/chkuendig/scummvm/commit/a55376a49748a99bc651402124097fd0efe56a71) EMSCRIPTEN: Exclude HTTP waits from recorder timing

## upstream/emscripten-printing

Review base: `upstream/master` (`ed949213a23`). 1 own commit(s), 1 including prerequisites.

- [36542d5a34a](https://github.com/chkuendig/scummvm/commit/36542d5a34a70b41429349e5a3fe4d706aac19b5) EMSCRIPTEN: Download game printouts in the browser

## upstream/emscripten-loading-progress

Review base: `upstream/master` (`ed949213a23`). 1 own commit(s), 1 including prerequisites.

- [af0715354f0](https://github.com/chkuendig/scummvm/commit/af0715354f01801869f10767d4ae9b0c3210f313) EMSCRIPTEN: Show download and initialization progress

## upstream/cloud-streaming

Review base: `upstream/emscripten-filesystem` (`a55376a4974`). 3 own commit(s), 7 including prerequisites.

- [36fb6e804b4](https://github.com/chkuendig/scummvm/commit/36fb6e804b4d48e22dfcb34ba7c48b9c9e169413) CLOUD: Add HTTP range downloads
- [da29b764ef6](https://github.com/chkuendig/scummvm/commit/da29b764ef6af657a29fa631c7371487463d91ee) CLOUD: Handle token refresh failures in browsers
- [989fab0127a](https://github.com/chkuendig/scummvm/commit/989fab0127adf774009e6b71e72b933d73f1d32f) EMSCRIPTEN: Use the shared cache for cloud files

## upstream/hpl1-webgl

Review base: `upstream/emscripten-opengl` (`69031266a7f`). 5 own commit(s), 9 including prerequisites.

- [d179546aac7](https://github.com/chkuendig/scummvm/commit/d179546aac748e9db635a02871ec447df1eadb4e) HPL1: Bundle shaders and adapt them for GLES
- [010a839e520](https://github.com/chkuendig/scummvm/commit/010a839e520efa3950f8b6d088445a037287c02c) HPL1: Add a GLES renderer for WebGL2
- [66878e6374c](https://github.com/chkuendig/scummvm/commit/66878e6374c5f54e77ec36fc558c3079c91a4a22) HPL1: Add gamepad bindings and menu navigation
- [b0412628bf6](https://github.com/chkuendig/scummvm/commit/b0412628bf62804bcd78d57668b4c4471be8edf5) KEYMAPPER: Add engine joystick-axis actions
- [7611209c905](https://github.com/chkuendig/scummvm/commit/7611209c9056d9735f98e7f8db275f41bc101068) HPL1: Add gamepad camera controls

## upstream/emscripten-recorder

Review base: `upstream/master` (`ed949213a23`). 3 own commit(s), 3 including prerequisites.

- [eb51c55ad4a](https://github.com/chkuendig/scummvm/commit/eb51c55ad4a0df31199c036462b35131e6f6c370) COMMON: Finalize wrapped recorder streams
- [212a9227e6d](https://github.com/chkuendig/scummvm/commit/212a9227e6d0ef4964b84134a3631787f123b7ce) EMSCRIPTEN: Support recording and replay in the browser
- [f7527a15f1e](https://github.com/chkuendig/scummvm/commit/f7527a15f1e4446bca84cee46e5a9691a1525db6) EMSCRIPTEN: Avoid recorder callbacks in the audio mixer

## upstream/touch-controls

Review base: `upstream/master` (`ed949213a23`). 3 own commit(s), 3 including prerequisites.

- [2b0e201fbed](https://github.com/chkuendig/scummvm/commit/2b0e201fbed01d6391269b37fa96fd64ff6db478) BACKENDS: Add shared on-screen controls and touch settings
- [f9594f3bcad](https://github.com/chkuendig/scummvm/commit/f9594f3bcad25619873d1455fdc99edbc5f23b05) BACKENDS: Unify touch switching and controller detection
- [20485f872b5](https://github.com/chkuendig/scummvm/commit/20485f872b55a0dfa50602889768d1f31eb5a967) BACKENDS: Emit joystick axes from on-screen controls

All 32 are cherry-picked into demo `0c0d5223713e69da854d849b85b65836b9a4c261`. See the [branch overview](upstream-pr-branches.md) for review order and validation limits.
