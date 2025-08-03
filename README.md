# ![ScummVM](logo.png) (unofficial) Web Demo
Demo page built with the new Emscripten backend for ScummVM. This is an unofficial demo until the backend is stable and feature-complete to be deployed in an official capacity.

## Status
Most features in ScummVM work, notably:
- All engines and their dependencies build and work, including 3D engines using WebGL (excl. enginees requiring Classic OpenGL).
- Cloud Integration to make it possible to play commercial games and sync savegames.
- Support for almost all sound options (excl. MT-32 emulation), including support for physical Retrowave OPL3 and MIDI devices via WebSerial and WebMIDI.
- Support for exporting logfiles and screenshots as file downloads.
- All tests in the [testbed engine](https://wiki.scummvm.org/index.php/HOWTO-Backends#Testing_your_backend) pass.
- 

For details, please check out the following write-ups:
- August 20, 2021: [Porting ScummVM to Webassembly](https://christian.kuendig.info/posts/2021-08-scummvm-wasm/)
- March 21, 2022: [Porting ScummVM to Webassembly, Part 2](https://christian.kuendig.info/posts/2022-05-scummvm-part2/)
- Jan 4, 2024: [Porting ScummVM to Webassembly, Part 3](https://christian.kuendig.info/posts/2024-01-scummvm-part3/)

## Getting Started
If you want to just try out the demo, go to [scummvm.kuendig.io](https://scummvm.kuendig.io). 

## Architecture

This repo builds and deploys four primary components:

- **ScummVM**: *(duh)* ScumMVM the executable, including all engines as plugins (having them hardlinked would end up with a 100M+ main executable - not great), and a default config scummmvm.ini so there's already some games when opening it. The [ScummVM Icons](https://github.com/chkuendig/scummvm-icons)) are also all bundled in this deployment. 
  
  Link: [scummvm.kuendig.io/scummvm.html](https://scummvm.kuendig.io/scummvm.html).

- **Games Overview**: A static page, containing all games available (see below), serving as an overview page to launch each and search them. Will also include some simple instructions and link to start ScummVM to the launch screen. 
  
  Link: [scummvm.kuendig.io/games.html](https://scummvm.kuendig.io/games.html).

- **Games Data**: All games are stored on a separate host, to make the deployment of other components easier (they can be atomic - e.g. delete everything and redeploy). This can be done by having the `index.json` in the data directory for ScummVM define a separate `baseURL` for the games subfolder. 
  
  Link: [scummvm-data.kuendig.io/index.json](https://scummvm-data.kuendig.io/index.json).

- **ScummVM Cloud**: Freeware and demos are only fun for so long. To allow users to bring commercial games they bought along, [ScummVM Cloud](https://github.com/chkuendig/scummvm-cloud) provides backend service to integrate with cloud storage providers (Google Drive, Dropbox, OneDrive, Box.com). **Please note that this Demo deployment uses separate App IDs with each cloud providers, so it can't access data from the native ScummVM App**. 
  
  Link: [scummvm-cloud.kuendig.io/](https://scummvm-cloud.kuendig.io/).


## Building
If you want to build this yourself, please check out the [README of the build scripts](scripts/README.md) and the [Emscripten README](https://github.com/chkuendig/scummvm/blob/emscripten/dists/emscripten/README.md) in the ScummVM source tree.