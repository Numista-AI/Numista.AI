const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const files = [
    { name: '1943_1c_obverse.jpg', wiki: 'File:1943s_steel_cent_obv.jpg' },
    { name: '1940_2c_obverse.jpg', wiki: 'File:1865_Two_Cent_Obverse.png' },
    { name: '1940_3c_obverse.jpg', wiki: 'File:NNC-US-1865-3C-Three-Cent,_Nickel_obverse_(cropped).jpg' }
];

const scratchDir = path.join(__dirname, 'scratch');

(async () => {
    console.log('Launching browser...');
    const browser = await chromium.launch();
    const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport: { width: 1280, height: 1024 }
    });

    for (const file of files) {
        const dest = path.join(scratchDir, file.name);
        const wikiUrl = `https://commons.wikimedia.org/wiki/${encodeURIComponent(file.wiki)}`;
        console.log(`Processing ${wikiUrl}...`);
        
        const page = await context.newPage();
        try {
            await page.goto(wikiUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
            
            const selectors = [
                '#file img',
                '.fullImage img',
                '.mw-file-description img'
            ];
            
            let element = null;
            for (const selector of selectors) {
                try {
                    element = await page.waitForSelector(selector, { timeout: 10000, state: 'visible' });
                    if (element) {
                        const box = await element.boundingBox();
                        if (box && box.width > 50 && box.height > 50) {
                            console.log(`  Found image with selector: ${selector} (${Math.round(box.width)}x${Math.round(box.height)})`);
                            break;
                        }
                    }
                } catch (e) {}
            }

            if (element) {
                await element.scrollIntoViewIfNeeded();
                await new Promise(r => setTimeout(r, 2000));
                await element.screenshot({ path: dest });
                console.log(`  Success (Screenshot): ${file.name} [${fs.statSync(dest).size} bytes]`);
            } else {
                console.log(`  Failed: No suitable image found for ${file.wiki}`);
            }
        } catch (e) {
            console.log(`  Error processing ${file.name}: ${e.message}`);
        }
        await page.close();
        await new Promise(r => setTimeout(r, 2000));
    }

    await browser.close();
    console.log('Done.');
})();
