const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const files = [
    { name: '2024_kennedy_half_obverse.jpg', wiki: 'File:Obverse of the 2021 John F. Kennedy Half Dollar.jpg' },
    { name: '2024_jefferson_nickel_obverse.jpg', wiki: 'File:Jefferson-Nickel-Obverse.jpg' },
    { name: '2024_lincoln_cent_obverse.png', wiki: 'File:US One Cent Obv.png' },
    { name: '2024_roosevelt_dime_obverse.jpg', wiki: 'File:United States dime, obverse, 2002.jpg' },
    { name: '1942_walking_liberty_obverse.jpg', wiki: 'File:1942 Walking Liberty Half Dollar Obverse.jpg' },
    { name: '1942_washington_quarter_obverse.jpg', wiki: 'File:Monnaie - Etats-Unis, 1-4 dollar, Philadelphie, 1942 - btv1b113366180.jpg' },
    { name: '1990_eisenhower_centennial_obverse.jpg', wiki: 'File:1990 Eisenhower Silver $1 Obverse.jpg' },
    { name: '1937_buffalo_nickel_obverse.jpg', wiki: 'File:Buffalo nickel obverse.jpg' },
    { name: '1951_franklin_half_obverse.jpg', wiki: 'File:Franklin half dollar obverse.jpg' },
    { name: '2023_kennedy_half_obverse.jpg', wiki: 'File:Obverse of the 2021 John F. Kennedy Half Dollar.jpg' },
    { name: '2022_jefferson_nickel_obverse.jpg', wiki: 'File:Jefferson-Nickel-Obverse.jpg' },
    { name: '2023_jefferson_nickel_obverse.jpg', wiki: 'File:Jefferson-Nickel-Obverse.jpg' },
    { name: '2022_lincoln_cent_obverse.png', wiki: 'File:US One Cent Obv.png' },
    { name: '2022_roosevelt_dime_obverse.jpg', wiki: 'File:United States dime, obverse, 2002.jpg' },
    { name: '2023_roosevelt_dime_obverse.jpg', wiki: 'File:United States dime, obverse, 2002.jpg' }
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
            
            // Find the "Original file" link
            const originalFileLink = await page.evaluate(() => {
                const link = document.querySelector('.fullMedia a');
                return link ? link.href : null;
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
