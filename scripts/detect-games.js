
const http = require('http');
const fs = require('fs');
const puppeteer = require('puppeteer');
const static = require('node-static');

var file = new static.Server("./", { headers: { 'Cross-Origin-Opener-Policy': 'same-origin','Cross-Origin-Embedder-Policy':'require-corp','Cross-Origin-Resource-Policy':'same-site' } });
const server = http.createServer(function (req, res) {
    req.addListener('end', function () {
        file.serve(req, res);
    }).resume();
}).listen({ host: 'localhost', port: 0 },async () => {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    await page.goto('http://localhost:' + server.address().port + '/scummvm.html#--add --path=/data/games --recursive');

    await page.screenshot({ path: 'example.png' });
    const regex = /Added ([0-9]+) games/;
    page.on('console', async msg => {
        const text = msg.text()
        console.log(text)
        const match = text.match(regex);
        if (match != null && match.length > 0) {
            console.log("Detection finished, exporting ini file for " + match[1] + " detected games.")
            const ini_file = await page.evaluate(() => {return FS.readFile("/home/web_user/scummvm.ini", { encoding: 'utf8' })});
            const ini_lines = ini_file.split('\n');
            // GRIM games check data consistency by reading all files. That's an expensive operation over
            // the network. Since we anyway should have known good data at build time, this script disables
            // that check.
            for (var i = 0; i < ini_lines.length; i++) {
                if (ini_lines[i] == "engineid=grim") {
                    ini_lines[i] = "check_gamedata=false\n" + ini_lines[i]
                }
            }
            fs.writeFileSync("scummvm.ini", ini_lines.join('\n'));
            browser.close();
            server.close();

            console.log('Done');
        }
    });


});