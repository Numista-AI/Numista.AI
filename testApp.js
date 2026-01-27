const fs = require('fs');
const path = require('path');
// Import the services we created
const { processInvoice } = require('./invoiceService');
const { mapToSchema } = require('./mappingController');

async function runTest() {
    try {
        console.log("🚀 Starting Coin App Test...");

        // 1. Path to your sample invoice
        const invoicePath = path.join(__dirname, 'sample-invoice.pdf');

        // Check if the PDF actually exists before trying to read it
        if (!fs.existsSync(invoicePath)) {
            console.error(`❌ ERROR: Could not find the file: ${invoicePath}`);
            console.log("Please ensure your invoice is named 'sample-invoice.pdf' and is in the project folder.");
            return;
        }

        const pdfBuffer = fs.readFileSync(invoicePath);

        // 2. Step 1: Scanning via Document AI
        console.log("📄 Step 1: Scanning Invoice via Document AI...");
        const entities = await processInvoice(pdfBuffer);
        console.log(`✅ Document processing complete. Extracted ${entities.length} entities.`);

        // 3. Step 2: Researching and Mapping via Gemini 3 Pro
        console.log("🧠 Step 2: Researching and Mapping via Gemini 2.5 Pro...");
        // ... this is where Gemini finishes mapping ...
        const finalCollection = await mapToSchema(entities);

        // 1. Log success to the terminal
        console.log("✨ Gemini Mapping Complete!");

        // 2. Import the server and hand over the data
        const { startReviewServer } = require('./server');

        // 3. This starts the web server and keeps the app running
        startReviewServer(finalCollection);

    } catch (error) {
        console.error("❌ Test Failed:", error.message);
    }
}

runTest();