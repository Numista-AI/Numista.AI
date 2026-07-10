const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const images = [
    { name: '1942_walking_liberty_obverse.jpg', url: 'https://upload.wikimedia.org/wikipedia/commons/4/4c/Walkinglibertyhalfdollar1.jpg' },
    { name: '1942_washington_quarter_obverse.jpg', url: 'https://upload.wikimedia.org/wikipedia/commons/2/25/Monnaie_-_Etats-Unis%2C_1-4_dollar%2C_Philadelphie%2C_1942_-_btv1b113366180_%281_of_2%29.jpg' },
    { name: '1990_eisenhower_centennial_obverse.jpg', url: 'https://upload.wikimedia.org/wikipedia/commons/6/67/1990_Eisenhower_Silver_%241_Obverse.jpg' },
    { name: '1937_buffalo_nickel_obverse.png', url: 'https://upload.wikimedia.org/wikipedia/commons/e/e0/Indian_Head_Nickel.png' },
    { name: '1951_franklin_half_obverse.png', url: 'https://upload.wikimedia.org/wikipedia/commons/d/df/Franklin_HalfObverse.png' },
    { name: '2024_kennedy_half_obverse.jpg', url: 'https://upload.wikimedia.org/wikipedia/commons/e/e7/Obverse_of_the_2021_John_F._Kennedy_Half_Dollar.jpg' },
    { name: '2024_jefferson_nickel_obverse.jpg', url: 'https://upload.wikimedia.org/wikipedia/commons/e/ee/Jefferson-Nickel-Obverse.jpg' },
    { name: '2024_lincoln_cent_obverse.png', url: 'https://upload.wikimedia.org/wikipedia/commons/e/e5/US_One_Cent_Obv.png' },
    { name: '2024_roosevelt_dime_obverse.jpg', url: 'https://upload.wikimedia.org/wikipedia/commons/a/a0/United_States_dime%2C_obverse%2C_2002.jpg' },
    { name: '2023_kennedy_half_obverse.png', url: 'https://upload.wikimedia.org/wikipedia/commons/e/e1/US_Half_Dollar_Obverse_2015.png' },
    { name: '2022_lincoln_cent_obverse.jpg', url: 'https://upload.wikimedia.org/wikipedia/commons/2/25/2018-S_proof_Lincoln_cent_obverse_%28reverse_cameo%29.jpg' },
    { name: '2022_jefferson_nickel_obverse.png', url: 'https://upload.wikimedia.org/wikipedia/commons/7/70/2013_P_Jefferson_nickel_obverse.png' },
    { name: '2023_jefferson_nickel_obverse.png', url: 'https://upload.wikimedia.org/wikipedia/commons/b/be/2005_Nickel_Obv_Unc_P.png' },
    { name: '2022_roosevelt_dime_obverse.png', url: 'https://upload.wikimedia.org/wikipedia/commons/a/a2/US_Dime_Obverse_2015.png' },
    { name: '2023_roosevelt_dime_obverse.png', url: 'https://upload.wikimedia.org/wikipedia/commons/0/05/Dime_Obverse_13.png' }
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
