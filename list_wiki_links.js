const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    await page.goto('https://commons.wikimedia.org/wiki/Category:Lincoln_cents');
    const links = await page.$$eval('a', as => as.map(a => a.href));
    const fileLinks = links.filter(l => l.includes('File:'));
    console.log(JSON.stringify(fileLinks, null, 2));
    await browser.close();
})();
