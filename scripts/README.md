# ScummVM Demo Scripts
This folder contains a set of scripts that help with setting up a demo environment for the ScummVM Web (Emscripten) Port. Best see the [Github Actions workflow].(.github/workflows/main.yml)  on how to chain these together.

## Scripts to build the demo deployment

### `sync-games.py/.sh`
Central synchronization tool for managing the ScummVM demo library between local development and remote hosting environments via scp. Downloads all demos and game downloads on the [ScummVM Data Google Sheet](https://docs.google.com/spreadsheets/d/e/2PACX-1vQamumX0p-DYQa5Umi3RxX-pHM6RZhAj1qvUP0jTmaqutN9FwzyriRSXlO9rq6kR60pGIuPvCDzZL3s/pub#) if they are in the compatibility table or manually included in  `assets/metadata.json`. Ensures no 'orphaned' folders remain on the remote servers, all folders are present and generates index.json for any folder that needs it. Also calls `sync-games-json` to create the `games.json` file required for the overview page.

*Example*:
```
python3 scripts/sync-games.py --max-transfers 1 --max-transfers 1 --scp-server user@host --scp-path /home/user/domains/domainname.com/public_html --scp-port 1337
```

### `sync-games-json.py`
Generates the `games.json` file required for the `games.html` overview page. This is a list of games that can be loaded over http. As with `sync-games.py`, games are collected from the remote sftp server, the [ScummVM Data Google Sheet](https://docs.google.com/spreadsheets/d/e/2PACX-1vQamumX0p-DYQa5Umi3RxX-pHM6RZhAj1qvUP0jTmaqutN9FwzyriRSXlO9rq6kR60pGIuPvCDzZL3s/pub#) and the content of `assets/metadata.json`.

*Example:*
```
python3 scripts/sync-games-gen-json.py --output games.json --scp-server user@host --scp-path /home/user/domains/domainname.com/public_html --scp-port 1337
```

### `update-icons.sh`
Both ScummVM as well as the `games.html` overview page rely on a catalog of xml metadata and icons to sort, categorize and display a list of games (cover, company, game name etc). This script generates the xml files in the scummvm-icons repository and copies them to `scummvm/build-emscripten/data/` along with the gui icons. Automatically updates xml files based on the contents of `assets/metadata`.json`.

*Example:*
```
scripts/update-icons.sh   
```

## Other (retired) scripts

### `download-games.js/.sh`
Downloads a specified list of games and extracts them to  `scummvm/build-emscripten/data/games`. When requesting testbed and playground3d, it will generate the data (not download them).
*Example:*
```
npm install . &&
scripts/download-games.sh \
    ft,grim/grim-win-demo1-en.zip,driller,comi/comi-win-large-demo-en.zip,warlock,sky/BASS-Floppy-1.3.zip,drascula/drascula-1.0.zip,monkey4/emi-win-demo-en.zip,feeble,queen/FOTAQ_Floppy.zip,ft,grim/grim-win-demo2-en.zip,lsl7,lure,myst,phantasmagoria,riven,tlj,sword2,sinistersix,"https://downloads.scummvm.org/frs/demos/hypno/wetlands-dos-demo1-en.zip",asylum 

```

### `autodetect-games.js/.sh`
Generates a scummvm.ini file with all the games present in the `scummvm/build-emscripten/data/games` directory. This scummvm.ini can be bundled at `scummvm/build-emscripten/` and will be downloaded on first launch to initiate the default user settings. This allows to "pre-populate" the ScummmVM launcher screen with a few games.

*Example:*
```
npm install . &&
scripts/autodetect-games.sh 
```


### `screenshot-demos.py`
Tests all demos available at https://scummvm-test.kuendig.io/games.html by loading them and taking a screenshot after 10 seconds. Screenshots are saved to ./screenshots with names based on the game path.
