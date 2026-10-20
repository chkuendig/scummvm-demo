# Upstream review commits

There are 23 commits across eight review series. Counts exclude the listed prerequisite branches; every series has at most five commits and every complete stack has at most ten. The SDK 6.0.13 bump and URL reload behavior are folded into existing update/cleanup commits.

## upstream/emscripten-update-cleanup

Review base: `upstream/master` (`71cb05b1c03`). 3 review commits, 3 including prerequisites.

- [350a7d43eae](https://github.com/chkuendig/scummvm/commit/350a7d43eae219c5f8d8e4bc4bb9b9c81be810e8) EMSCRIPTEN: Extract JavaScript APIs and tidy browser integration
- [42f25c624fc](https://github.com/chkuendig/scummvm/commit/42f25c624fc05c1e3e4b2b801c179c8ac8cb1089) EMSCRIPTEN: Update SDK, dependencies and Asyncify build handling
- [d6b65d41d68](https://github.com/chkuendig/scummvm/commit/d6b65d41d683724dada5b4573ebb94f47e39ce46) EMSCRIPTEN: Scope WebGL rendering fixes to the browser

## upstream/emscripten-filesystem

Review base: `upstream/emscripten-update-cleanup` (`d6b65d41d68`). 3 review commits, 6 including prerequisites.

- [63963bcfa73](https://github.com/chkuendig/scummvm/commit/63963bcfa7322eb8d9092d2a6554ecd623d8d9e5) EMSCRIPTEN: Stream HTTP files through a bounded virtual filesystem
- [9df5ba64d3b](https://github.com/chkuendig/scummvm/commit/9df5ba64d3bbe9e39f760545eab6e5f18ed20e1d) EMSCRIPTEN: Mount dropped files and import Roland ROMs
- [02ae5145991](https://github.com/chkuendig/scummvm/commit/02ae5145991b9ea9c1754f12a381650ec7bb5f75) EMSCRIPTEN: Persist settings storage and use supported FS APIs

## upstream/emscripten-printing

Review base: `upstream/emscripten-update-cleanup` (`d6b65d41d68`). 1 review commit, 4 including prerequisites.

- [aa6e5dc729e](https://github.com/chkuendig/scummvm/commit/aa6e5dc729e5d6f57e2693b49f177726e9ea686e) EMSCRIPTEN: Download game print-outs through the browser

## upstream/emscripten-loading-progress

Review base: `upstream/emscripten-update-cleanup` (`d6b65d41d68`). 1 review commit, 4 including prerequisites.

- [13cbcd7458c](https://github.com/chkuendig/scummvm/commit/13cbcd7458cdd12bcbd988ef0e57b97196f7a110) EMSCRIPTEN: Show download and initialization progress

## upstream/cloud-streaming

Review base: `upstream/emscripten-filesystem` (`02ae5145991`). 3 review commits, 9 including prerequisites.

- [1d3cf709cda](https://github.com/chkuendig/scummvm/commit/1d3cf709cda21ee7a7e7e2f49036610a5edba402) CLOUD: Support efficient ranged downloads
- [649517c6314](https://github.com/chkuendig/scummvm/commit/649517c63144a712a14ee6eaf0828904f6850f0e) CLOUD: Handle access tokens and browser refresh failures
- [5718ef42c81](https://github.com/chkuendig/scummvm/commit/5718ef42c81b98854c0957d253153cec0215566a) EMSCRIPTEN: Stream cloud files through the shared filesystem

## upstream/hpl1-webgl

Review base: `upstream/emscripten-update-cleanup` (`d6b65d41d68`). 5 review commits, 8 including prerequisites.

- [6a9dc7caac9](https://github.com/chkuendig/scummvm/commit/6a9dc7caac99d4cf7f1bbc7360f1a1c35b30b75a) HPL1: Bundle shaders and adapt them for GLES
- [4c24e3bc951](https://github.com/chkuendig/scummvm/commit/4c24e3bc95137dd7e75a5925988897c90c7ba216) HPL1: Add the WebGL2 renderer and GLES compatibility layer
- [57d60d3da7c](https://github.com/chkuendig/scummvm/commit/57d60d3da7ca93777e57fa41e69d1a38fe7a4181) HPL1: Add controller bindings and menu focus navigation
- [9b8eaae24c0](https://github.com/chkuendig/scummvm/commit/9b8eaae24c0b01e162f7dfc6fea2c4ce3a8de28a) KEYMAPPER: Provide shared engine-axis actions for HPL1
- [a4358d6b082](https://github.com/chkuendig/scummvm/commit/a4358d6b082d052d6cb49df36f8b488ccccc893a) HPL1: Handle native camera axes and preserve touch response

## upstream/emscripten-recorder

Review base: `upstream/emscripten-filesystem` (`02ae5145991`). 4 review commits, 10 including prerequisites.

- [d731e04f1eb](https://github.com/chkuendig/scummvm/commit/d731e04f1eb3bb67cd9e00c8f508d3c5640c6309) COMMON: Propagate finalize() through buffered and recorder write streams
- [ab65a7cd589](https://github.com/chkuendig/scummvm/commit/ab65a7cd589c66783e5c54629dc3ddf7daf644cd) BACKENDS: EMSCRIPTEN: Make the event recorder work on the web port
- [0dc4b6c78da](https://github.com/chkuendig/scummvm/commit/0dc4b6c78da6f50b6d50d35ddad2cfc89210e5b2) GUI: Fit web recorder controls to the letterboxed game area
- [3e3831a6ba8](https://github.com/chkuendig/scummvm/commit/3e3831a6ba8620c532c8f3c7bd0af7669a012d38) BACKENDS: EMSCRIPTEN: Keep the SDL audio callback out of the event recorder

## upstream/touch-controls

Review base: `upstream/master` (`71cb05b1c03`). 3 review commits, 3 including prerequisites.

- [192858a8587](https://github.com/chkuendig/scummvm/commit/192858a858733b4bb266fef43d06cb09871da60f) BACKENDS: Add shared on-screen controls and touch preferences
- [ab0a58104f0](https://github.com/chkuendig/scummvm/commit/ab0a58104f0a285e6cd5659e487ef49ec0933f54) BACKENDS: Harmonize controller availability and touch switching
- [8ef1023b2b8](https://github.com/chkuendig/scummvm/commit/8ef1023b2b8ee6413c44e76f1e3ca4abfbf54246) BACKENDS: Emit touch joystick axes with the established response
