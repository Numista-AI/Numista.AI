const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const files = [
    { name: '1942_walking_liberty_obverse.jpg', wiki: 'File:Walkinglibertyhalfdollar1.jpg' },
    { name: '1942_washington_quarter_obverse.jpg', wiki: 'File:Monnaie_-_Etats-Unis,_1-4_dollar,_Philadelphie,_1942_-_btv1b113366180_(1_of_2).jpg' },
    { name: '1990_eisenhower_centennial_obverse.jpg', wiki: 'File:1990_Eisenhower_Silver_$1_Obverse.jpg' },
    { name: '1937_buffalo_nickel_obverse.png', wiki: 'File:Indian_Head_Nickel.png' },
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
    { name: '2023_roosevelt_dime_obverse.png', wiki: 'File:Dime_Obverse_13.png' }
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
        
        // Remove existing 429 error files
        if (fs.existsSync(dest) && fs.statSync(dest).size < 10000) {
            fs.unlinkSync(dest);
        }

        if (fs.existsSync(dest)) {
            console.log(`Skipping ${file.name} (already exists)`);
            continue;
        }

        const wikiUrl = `https://commons.wikimedia.org/wiki/${encodeURIComponent(file.wiki)}`;
        console.log(`Processing ${wikiUrl}...`);
        
        const page = await context.newPage();
        try {
            const response = await page.goto(wikiUrl, { waitUntil: 'networkidle', timeout: 60000 });
            
            if (response.status() === 429) {
                console.log('  Rate limited! Waiting 30 seconds...');
                await new Promise(r => setTimeout(r, 30000));
                await page.reload({ waitUntil: 'networkidle' });
            }

            // Wait for the image container - try multiple selectors
            const imgSelector = '.fullImage img, .mw-file-description img';
            await page.waitForSelector(imgSelector, { timeout: 20000 });
            
            const element = await page.$(imgSelector);
            if (element) {
                await element.screenshot({ path: dest });
                console.log(`  Success (Screenshot): ${file.name}`);
            } else {
                console.log(`  Failed: Could not find image element for ${file.wiki}`);
            }
        } catch (e) {
            console.log(`  Error processing ${file.name}: ${e.message}`);
            // If we failed, maybe save a whole page screenshot for debugging
            await page.screenshot({ path: path.join(scratchDir, `debug_${file.name}.png`) });
        }
        await page.close();
        await new Promise(r => setTimeout(r, 10000)); // Be VERY polite
    }

    await browser.close();
    console.log('Done.');
})();
