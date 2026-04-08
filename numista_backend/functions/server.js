const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
const app = express();

// 1. Configure Express to use EJS templates
app.set('view engine', 'ejs');
// UPDATED: Use path.join to correctly locate views in the functions environment
app.set('views', path.join(__dirname, 'views'));

// Serve static files from the 'public' directory
// Note: In Firebase Hosting, static files are usually served by hosting, but this helps for local dev/fallbacks
app.use(express.static(path.join(__dirname, '../public')));

// 2. Middleware to handle form data (extended: true is required for nested objects)
app.use(bodyParser.urlencoded({ extended: true }));

// 3. Temporary storage for the AI-extracted data
let stagedData = [];

// --- GUEST FEATURE ROUTES ---

/**
 * Route: Landing Page
 */
app.get('/', (req, res) => {
    res.render('index');
});

/**
 * Route: Guest Collection
 */
app.get('/guest', (req, res) => {
    // Dummy data for the guest experience
    const dummyCoins = [
        { name: 'Lincoln Wheat Cent', year: 1909, country: 'USA', composition: '95% Copper', grade: 'MS-63 RB', value: 45.00 },
        { name: 'Morgan Silver Dollar', year: 1881, country: 'USA', composition: '90% Silver', grade: 'MS-65', value: 250.00 },
        { name: 'Walking Liberty Half', year: 1942, country: 'USA', composition: '90% Silver', grade: 'AU-58', value: 35.00 },
        { name: 'Mercury Dime', year: 1945, country: 'USA', composition: '90% Silver', grade: 'MS-67 FB', value: 120.00 },
        { name: 'Indian Head Cent', year: 1877, country: 'USA', composition: 'Bronze', grade: 'G-4', value: 650.00 },
        { name: 'Buffalo Nickel', year: 1913, country: 'USA', composition: 'Cupro-Nickel', grade: 'VF-20', value: 15.00 },
        { name: 'Saint-Gaudens Double Eagle', year: 1924, country: 'USA', composition: '90% Gold', grade: 'MS-62', value: 2300.00 },
        { name: 'Peace Dollar', year: 1922, country: 'USA', composition: '90% Silver', grade: 'MS-64', value: 55.00 }
    ];

    const totalValue = dummyCoins.reduce((sum, coin) => sum + coin.value, 0);

    res.render('guest_collection', { coins: dummyCoins, totalValue });
});

// ----------------------------

/**
 * Route: Display the Review Page
 * This renders the review.ejs file with the data Gemini found
 */
app.get('/review', (req, res) => {
    if (stagedData.length === 0) {
        return res.send("<h1>No data found.</h1><p>Please run testApp.js again to scan an invoice.</p>");
    }
    res.render('review', { coins: stagedData });
});

/**
 * Route: Handle Final Submission
 * Triggered when you click "✅ Looks Good, Save to Database"
 */
app.post('/submit-to-db', (req, res) => {
    // Get raw data from the web form
    const rawCoins = req.body.coins;

    if (!rawCoins) {
        return res.send("<h1>No coins were submitted.</h1><a href='/review'>Go Back</a>");
    }

    // CLEANUP: If you deleted coins, the array might have "gaps" or be an object.
    // This logic ensures we get a clean list of verified coin objects.
    const verifiedCoins = Object.values(rawCoins).filter(coin => coin !== null);

    console.log("\n" + "=".repeat(40));
    console.log("📦 FINAL VERIFIED DATA FOR DATABASE:");
    console.log("=".repeat(40));
    console.log(JSON.stringify(verifiedCoins, null, 2));

    // --- FUTURE FIREBASE LOGIC ---
    // Soon, we will add: verifiedCoins.forEach(coin => db.collection('coins').add(coin));
    // ------------------------------

    res.send(`
        <div style="text-align:center; padding:50px; font-family:sans-serif; background:#f0f2f5; min-height:100vh;">
            <div style="background:white; padding:40px; border-radius:12px; display:inline-block; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
                <h1 style="color:#28a745; margin-top:0;">✅ Data Successfully Verified!</h1>
                <p style="font-size:18px;">Your batch of <strong>${verifiedCoins.length}</strong> coins has been processed.</p>
                <p style="color:#666;">Check your terminal to see the final JSON payload.</p>
                <br>
                <a href="/review" style="text-decoration:none; color:#1a73e8; font-weight:bold;">← Process Another Invoice</a>
            </div>
        </div>
    `);
});

/**
 * Function to start the local web server
 * Called by testApp.js after Gemini finishes mapping
 */
function startReviewServer(data) {
    // Ensure data is an array (Gemini might return a single object)
    if (data) {
        stagedData = Array.isArray(data) ? data : [data];
    }

    // Check if we are in Cloud Functions environment (no listening needed)
    if (process.env.FUNCTIONS_EMULATOR || process.env.FIREBASE_CONFIG) {
        return app;
    }

    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
        console.log("\n" + "=".repeat(50));
        console.log(`🌐 NUMISTA.AI IS LIVE!`);
        console.log(`Landing Page: http://localhost:${PORT}/`);
        console.log(`Guest Mode:   http://localhost:${PORT}/guest`);
        if (stagedData.length > 0) {
            console.log(`Review Page:  http://localhost:${PORT}/review`);
        }
        console.log(`(Press Ctrl + C in this terminal to stop the server)`);
        console.log("=".repeat(50) + "\n");
    });
}

// Export the app for Cloud Functions
module.exports = app;

// Also export the start function for local scripts
module.exports.startReviewServer = startReviewServer;

// Check if this module is being run directly (e.g., node server.js)
if (require.main === module) {
    startReviewServer();
}