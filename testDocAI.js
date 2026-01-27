const fs = require('fs');
const path = require('path');
const { processInvoice } = require('./invoiceService');

async function testDocAI() {
    console.log("📄 Testing Document AI...");
    try {
        const invoicePath = path.join(__dirname, 'sample-invoice.pdf');
        if (!fs.existsSync(invoicePath)) {
            console.error("❌ Sample invoice not found!");
            return;
        }
        const pdfBuffer = fs.readFileSync(invoicePath);
        const entities = await processInvoice(pdfBuffer);
        console.log(`✅ Success! Extracted ${entities.length} entities.`);
        console.log(JSON.stringify(entities, null, 2));
    } catch (error) {
        console.error("❌ Document AI Failed:", error);
    }
}

testDocAI();
