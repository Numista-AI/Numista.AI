const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const files = [
    { name: '1942_walking_liberty_obverse.jpg', wiki: 'File:Walkinglibertyhalfdollar2.jpg' }, // Switched back to one that was on the page
    { name: '1942_washington_quarter_obverse.jpg', wiki: 'File:Monnaie_-_Etats-Unis,_1-4_dollar,_Philadelphie,_1942_-_btv1b113366180_(1_of_2).jpg' },
    { name: '1990_eisenhower_centennial_obverse.jpg', wiki: 'File:1990_Eisenhower_Silver_$1_Obverse.jpg' },
    { name: '1937_buffalo_nickel_obverse.png', wiki: 'File:Indian_Head_Buffalo_Obverse.jpg' },
    { name: '1951_franklin_half_obverse.png', wiki: 'File:Franklin_HalfObverse.png' },
    { name: '2024_kennedy_half_obverse.jpg', wiki: 'File:Obverse_of_the_2021_John_F._Kennedy_Half_Dollar.jpg' },
    { name: '2024_jefferson_nickel_obverse.jpg', wiki: 'File:United_States_nickel_obverse.jpg' },
    { name: '2024_lincoln_cent_obverse.png', wiki: 'File:US_One_Cent_Obv.png' },
    { name: '2024_roosevelt_dime_obverse.jpg', wiki: 'File:United_States_dime,_obverse,_2002.jpg' },
    { name: '2023_kennedy_half_obverse.png', wiki: 'File:US_Half_Dollar_Obverse_2015.png' },
    { name: '2022_lincoln_cent_obverse.jpg', wiki: 'File:2018-S_proof_Lincoln_cent_obverse_(reverse_cameo).jpg' },
    { name: '2022_jefferson_nickel_obverse.png', wiki: 'File:2013_P_Jefferson_nickel_obverse.png' },
    { name: '2023_jefferson_nickel_obverse.png', wiki: 'File:2005_Nickel_Obv_Unc_P.png' },
    { name: '2022_roosevelt_dime_obverse.png', wiki: 'File:US_Dime_Obverse_2015.png' },
    { name: '2023_roosevelt_dime_obverse.png', wiki: 'File:Dime_Obverse_13.png' },
    { name: '1943_1c_obverse.jpg', wiki: 'File:1943_Lincoln_Cent_Obverse.jpg' },
    { name: '1940_2c_obverse.jpg', wiki: 'File:United_States_Two-Cent_Piece_Obverse.png' },
    { name: '1940_3c_obverse.jpg', wiki: 'File:US_Three_Cent_Nickel_Obv.png' }
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
        
        // Skip only if significantly large (> 10KB)
        if (fs.existsSync(dest) && fs.statSync(dest).size > 10000) {
            console.log(`Skipping ${file.name} (already exists)`);
            continue;
        }

        const wikiUrl = `https://commons.wikimedia.org/wiki/${encodeURIComponent(file.wiki)}`;
        console.log(`Processing ${wikiUrl}...`);
        
        const page = await context.newPage();
        try {
            // Faster load
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
                        if (box && box.width > 50 && box.height > 50) { // Slightly more lenient size
                            console.log(`  Found image with selector: ${selector} (${Math.round(box.width)}x${Math.round(box.height)})`);
                            break;
                        } else {
                            console.log(`  Selector ${selector} found but too small`);
                            element = null;
                        }
                    }
                } catch (e) {}
            }

            if (element) {
                await element.scrollIntoViewIfNeeded();
                await new Promise(r => setTimeout(r, 1000));
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
