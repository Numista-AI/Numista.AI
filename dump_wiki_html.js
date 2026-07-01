const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    await page.goto('https://commons.wikimedia.org/wiki/File:Walking_Liberty_half_dollar_obverse.jpg');
    const html = await page.content();
    fs.writeFileSync('wiki_page_debug.html', html);
    await browser.close();
    console.log('Saved wiki_page_debug.html');
})();
