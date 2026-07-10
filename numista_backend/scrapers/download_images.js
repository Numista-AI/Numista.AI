const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const images = [
    { name: '2024_kennedy_half_obverse.jpg', url: 'https://upload.wikimedia.org/wikipedia/commons/2/2b/Obverse_of_the_2021_John_F._Kennedy_Half_Dollar.jpg' },
    { name: '2024_jefferson_nickel_obverse.jpg', url: 'https://upload.wikimedia.org/wikipedia/commons/e/ee/Jefferson-Nickel-Obverse.jpg' },
    { name: '2024_lincoln_cent_obverse.png', url: 'https://upload.wikimedia.org/wikipedia/commons/0/07/US_One_Cent_Obv.png' },
    { name: '2024_roosevelt_dime_obverse.jpg', url: 'https://upload.wikimedia.org/wikipedia/commons/3/3c/United_States_dime%2C_obverse%2C_2002.jpg' },
    { name: '1942_walking_liberty_obverse.jpg', url: 'https://upload.wikimedia.org/wikipedia/commons/7/7b/1942_Walking_Liberty_Half_Dollar_Obverse.jpg' },
    { name: '1942_washington_quarter_obverse.jpg', url: 'https://upload.wikimedia.org/wikipedia/commons/7/77/Monnaie_-_Etats-Unis%2C_1-4_dollar%2C_Philadelphie%2C_1942_-_btv1b113366180.jpg' },
    { name: '1990_eisenhower_centennial_obverse.jpg', url: 'https://upload.wikimedia.org/wikipedia/commons/d/da/1990_Eisenhower_Silver_%241_Obverse.jpg' },
    { name: '1937_buffalo_nickel_obverse.jpg', url: 'https://upload.wikimedia.org/wikipedia/commons/a/ae/Buffalo_nickel_obverse.jpg' },
    { name: '1951_franklin_half_obverse.jpg', url: 'https://upload.wikimedia.org/wikipedia/commons/d/d7/Franklin_half_dollar_obverse.jpg' },
    { name: '2023_kennedy_half_obverse.jpg', url: 'https://upload.wikimedia.org/wikipedia/commons/2/2b/Obverse_of_the_2021_John_F._Kennedy_Half_Dollar.jpg' },
    { name: '2022_jefferson_nickel_obverse.jpg', url: 'https://upload.wikimedia.org/wikipedia/commons/e/ee/Jefferson-Nickel-Obverse.jpg' },
    { name: '2023_jefferson_nickel_obverse.jpg', url: 'https://upload.wikimedia.org/wikipedia/commons/e/ee/Jefferson-Nickel-Obverse.jpg' },
    { name: '2022_lincoln_cent_obverse.png', url: 'https://upload.wikimedia.org/wikipedia/commons/0/07/US_One_Cent_Obv.png' },
    { name: '2022_roosevelt_dime_obverse.jpg', url: 'https://upload.wikimedia.org/wikipedia/commons/3/3c/United_States_dime%2C_obverse%2C_2002.jpg' },
    { name: '2023_roosevelt_dime_obverse.jpg', url: 'https://upload.wikimedia.org/wikipedia/commons/3/3c/United_States_dime%2C_obverse%2C_2002.jpg' }
];

const scratchDir = path.join(__dirname, 'scratch');
if (!fs.existsSync(scratchDir)) {
    fs.mkdirSync(scratchDir);
}

(async () => {
    console.log('Launching browser...');
    const browser = await chromium.launch();
    const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });

    for (const image of images) {
        const dest = path.join(scratchDir, image.name);
        console.log(`Downloading ${image.url} to ${dest}...`);
        try {
            const page = await context.newPage();
            const response = await page.goto(image.url, { waitUntil: 'networkidle', timeout: 60000 });
            if (response.status() === 200) {
                const buffer = await response.body();
                fs.writeFileSync(dest, buffer);
                console.log(`  Success: ${image.name}`);
            } else {
                console.log(`  Failed with status ${response.status()}: ${image.url}`);
            }
            await page.close();
        } catch (e) {
            console.log(`  Error: ${e.message}`);
        }
    }

    await browser.close();
    console.log('Done.');
})();
