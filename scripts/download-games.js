const fs = require('fs');
const fsprocess = require('process');
const { pipeline } = require('stream/promises');

process.on('uncaughtException', (err, origin) => {
    console.error(err)
    console.error(origin)
    process.exitCode = 2
})
const args_games = process.argv.slice(2).filter((gameId) => gameId != "testbed" && gameId != "playground3d");

/*
 Copied from https://github.com/scummvm/scummvm-web/blob/master/include/DataUtils.php
 */
const SHEET_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQamumX0p-DYQa5Umi3RxX-pHM6RZhAj1qvUP0jTmaqutN9FwzyriRSXlO9rq6kR60pGIuPvCDzZL3s/pub?output=tsv';
const SHEET_IDS = {
    'platforms': '1061029686',
    'compatibility': '1989596967',
    'games': '1775285192',
    'engines': '0',
    'companies': '226191984',
    'versions': '1225902887',
    'game_demos': '1303420306',
    'series': '1095671818',
    'screenshots': '168506355',
    'scummvm_downloads': '1057392663',
    'game_downloads': '810295288',
    'director_demos': '1256563740',
}

// Helper function to handle redirects and fetch Google Sheets
async function getGoogleSheet(url) {
    const response = await fetch(url, {
        redirect: 'manual'
    });
    
    if (response.status >= 300 && response.status < 400 && response.headers.get('location')) {
        const redirectResponse = await fetch(response.headers.get('location'), {
            redirect: 'manual'
        });
        return await redirectResponse.text();
    }
    
    return await response.text();
}
function parseTSV(text) {
    const lines = text.split("\r\n")
    const headers = lines[0].split("\t")
    var ret = []
    for (var i = 1; i < lines.length; i++) {
        ret[i - 1] = {}
        lines[i].split("\t").forEach((value, col) => ret[i - 1][headers[col]] = value)
    }
    return ret
}

var games = {}
// Get Freeware Games
async function get_freeware_games() {
    console.error("download-games.js: Fetching list of freeware games")
    try {
        var url = SHEET_URL + "&gid=" + SHEET_IDS['game_downloads'];
        const body = await getGoogleSheet(url);
        parseTSV(body).forEach((downloads) => {
            var gameId = downloads['game_id'];
            if (downloads['category'] == "games" && !(gameId in games)) {
                games[gameId] = "/frs/extras/" + downloads['url']
                games[gameId.substring(gameId.lastIndexOf(":") + 1)] = "/frs/extras/" + downloads['url'] // allow specifying game names without target/engine name
            }
            filename = downloads['url'].substring(downloads['url'].lastIndexOf("/"))
            games[gameId + filename] = "/frs/extras/" + downloads['url']
            games[gameId.substring(gameId.lastIndexOf(":") + 1) + filename] = "/frs/extras/" + downloads['url'] // allow specifying game names without target/engine name
        })
    } catch (error) {
        throw error;
    }
}
// Get Demos Games
async function get_demos() {
    console.error("download-games.js: Fetching list of game demos")
    try {
        var url = SHEET_URL + "&gid=" + SHEET_IDS['game_demos'];
        const body = await getGoogleSheet(url);
        parseTSV(body).forEach((downloads) => {
            var gameId = downloads['id']
            if (!(gameId in games)) {
                games[gameId] = downloads['url']
                games[gameId.substring(gameId.lastIndexOf(":") + 1)] = downloads['url'] // allow specifying game names without target/engine name
            }
            filename = downloads['url'].substring(downloads['url'].lastIndexOf("/"))
            games[gameId + filename] = downloads['url']
            games[gameId.substring(gameId.lastIndexOf(":") + 1) + filename] = downloads['url'] // allow specifying game names without target/engine name
        })
    } catch (error) {
        throw error;
    }
}
// Get Director Demos 
async function get_director_demos() {
    console.error("download-games.js: Fetching list of director demos")
    try {
        var url = SHEET_URL + "&gid=" + SHEET_IDS['director_demos'];
        const body = await getGoogleSheet(url);
        if (body === undefined) {
            throw new Error('Failed to fetch director demos');
        }
        parseTSV(body).forEach((downloads) => {
            var gameId = downloads['id']
            if (!(gameId in games)) {
                games[gameId] = downloads['url']
                games[gameId.substring(gameId.lastIndexOf(":") + 1)] = downloads['url'] // allow specifying game names without target/engine name
            }
            filename = downloads['url'].substring(downloads['url'].lastIndexOf("/"))
            games[gameId + filename] = downloads['url']
            games[gameId.substring(gameId.lastIndexOf(":") + 1) + filename] = downloads['url'] // allow specifying game names without target/engine name
        });
    } catch (error) {
        throw error;
    }
}

// Download a file
async function download_file(uri, filename) {
    try {
        const response = await fetch(uri);
        
        if (response.status === 200) {
            console.error("download-games.js: Downloading " + uri);
            await pipeline(response.body, fs.createWriteStream(filename));
        } else {
            console.error(response);
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        throw error;
    }
}

const download_all_games = async (gameIds) => {
    for (var gameId of gameIds) {
        if (gameId.startsWith("http")) {
            var url = gameId
            var filename = url.substring(url.lastIndexOf("/") + 1)
            console.log(filename)
            if (!fs.existsSync(filename)) {
                await download_file(url, filename)
            }
        } else if (!(gameId in games)) {
            console.error("download-games.js: GameID " + gameId + " not known")
            process.exit(1)
        } else {
            var url = "https://downloads.scummvm.org" + games[gameId]
            if (gameId.includes("/")) {
                gameId = gameId.substring(0, gameId.lastIndexOf("/"))
            }
            gameId = gameId.substring(gameId.lastIndexOf(":") + 1)// remove target from target:gameId
            var filename = url.substring(url.lastIndexOf("/") + 1)
            if (!filename.startsWith(gameId)) { filename = gameId + "-" + filename }
            console.log(filename)
            if (!fs.existsSync(filename)) {
                await download_file(url, filename)
            }
        }
    }
}

// start everything
(async () => {
    try {
        await get_freeware_games();
        await get_demos();
        await get_director_demos();
        await download_all_games(args_games);
    } catch (error) {
        console.error('Error:', error);
        process.exit(1);
    }
})();
