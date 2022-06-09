# Emscripten Patches for ScummVM

This folder contains a few patches required to build ScummVM for WebAssembly with Emscripten 3.1.8:
 - **[emscripten-15893.patch](emscripten-15893.patch):** PR emscripten-core/emscripten#15893 rebased to version 3.1.8 (see [chkuendig/emscripten@asyncify-side-module-3.1.8](https://github.com/chkuendig/emscripten/tree/asyncify-side-module-3.1.8)).
 - **[emscripten-16559.patch](emscripten-16559.patch)**: PR emscripten-core/emscripten#16559.
 - **[emscripten-16687.patch](emscripten-16687.patch)**: PR emscripten-core/emscripten#16687.
 - **[libmad-0.15.1b-fixes-1.patch](libmad-0.15.1b-fixes-1.patch)**: see https://stackoverflow.com/questions/14015747/gccs-fforce-mem-option.

ScummVM also builds without these, but some features wont work.