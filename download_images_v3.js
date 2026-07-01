const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const files = [
    { name: '2024_jefferson_nickel_obverse.jpg', wiki: 'File:United States nickel obverse.jpg' },
    { name: '2023_jefferson_nickel_obverse.jpg', wiki: 'File:United States nickel obverse.jpg' },
    { name: '2022_jefferson_nickel_obverse.jpg', wiki: 'File:United States nickel obverse.jpg' },
    { name: '1942_walking_liberty_obverse.jpg', wiki: 'File:1942 Walking Liberty half dollar obverse.jpg' },
    { name: '1942_washington_quarter_obverse.jpg', wiki: 'File:1944 Washington quarter obverse.jpg' }, // 1942 was hard to find, 1944 is identical design
    { name: '1937_buffalo_nickel_obverse.jpg', wiki: 'File:Buffalo nickel obverse.jpg' },
    { name: '1951_franklin_half_obverse.jpg', wiki: 'File:Franklin half dollar obverse.jpg' }
];

const scratchDir = path.join(__dirname, 'scratch');
if (!fs.existsSync(scratchDir)) {
    fs.mkdirSync(scratchDir);
}

(async () => {
    console.log('Launching browser...');
    const browser = await chromium.launch();
    const context = await browser.newContext();

    for (const file of files) {
        const dest = path.join(scratchDir, file.name);
        const wikiUrl = `https://commons.wikimedia.org/wiki/${encodeURIComponent(file.wiki)}`;
        console.log(`Processing ${wikiUrl}...`);
        
        try {
            const page = await context.newPage();
            await page.goto(wikiUrl, { waitUntil: 'domcontentloaded' });
            
            // Try multiple selectors for the original file link
            const originalFileLink = await page.evaluate(() => {
                const fullMediaLink = document.querySelector('.fullMedia a');
                if (fullMediaLink) return fullMediaLink.href;
                
                const internalLink = document.querySelector('a.internal');
                if (internalLink) return internalLink.href;

                return null;
            });

            if (originalFileLink) {
                console.log(`  Downloading ${originalFileLink}...`);
                const response = await page.goto(originalFileLink);
                const buffer = await response.body();
                fs.writeFileSync(dest, buffer);
                console.log(`  Success: ${file.name}`);
            } else {
                console.log(`  Failed: Could not find original file link for ${file.wiki}`);
            }
            await page.close();
        } catch (e) {
            console.log(`  Error: ${e.message}`);
        }
    }

    await browser.close();
    console.log('Done.');
})();
