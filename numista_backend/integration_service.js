/**
 * integration_service.js
 * 
 * Main integration entry point.
 * Examples of capabilities:
 * 1. Verify coin authenticity using Vertex AI.
 * 2. Process an Invoice PDF using Document AI.
 */

const genaiPackage = require('@google/genai');
const GoogleGenAI = genaiPackage.GoogleGenAI;
const admin = require('firebase-admin');
const { processInvoice } = require('./invoiceService');
const fs = require('fs');

// Initialize Configuration
const PROJECT_ID = 'studio-9101802118-8c9a8';
const MODEL_NAME = 'gemini-2.5-flash';

// Initialize Firebase
try {
    admin.initializeApp({
        projectId: PROJECT_ID
    });
} catch (e) { }
const db = admin.firestore();

// Initialize Google GenAI
const genai = new GoogleGenAI();

/**
 * Verifies coin authenticity using Gemini.
 * @param {string} coinDescription - Text description of the coin.
 * @param {string} [imageBase64] - Optional base64 image of the coin.
 */
async function verifyCoinAuthenticity(coinDescription, imageBase64) {
    console.log(`Analyzing coin: ${coinDescription}...`);

    const parts = [{ text: `Verify the authenticity of this coin based on the description. Return a 'Confidence Score' and 'Key Indicators'. Description: ${coinDescription}` }];

    if (imageBase64) {
        parts.push({
            inlineData: {
                mimeType: 'image/jpeg',
                data: imageBase64
            }
        });
    }

    try {
        const result = await genai.models.generateContent({
            model: MODEL_NAME,
            contents: [{ role: 'user', parts }]
        });
        
        const text = result.text;

        console.log("--- Gemini AI Analysis ---");
        console.log(text);

        return text;
    } catch (error) {
        console.error("Verification failed:", error);
    }
}

/**
 * Example usage runner.
 * Pass 'invoice <file>' or 'verify <desc>' arguments.
 */
async function main() {
    const args = process.argv.slice(2);
    const command = args[0];

    if (command === 'invoice') {
        const filePath = args[1];
        if (!filePath) { console.log("Provide file path."); return; }
        const buffer = fs.readFileSync(filePath);
        const entities = await processInvoice(buffer);
        console.log("Extracted Entities:", JSON.stringify(entities, null, 2));

    } else if (command === 'verify') {
        const desc = args.slice(1).join(' '); // Join remaining args as description
        if (!desc) { console.log("Provide description."); return; }
        await verifyCoinAuthenticity(desc);

    } else {
        console.log("Usage:");
        console.log("  node integration_service.js invoice <path-to-pdf>");
        console.log("  node integration_service.js verify <coin-description>");
        console.log("  node import_excel.js <path-to-excel> (Separate Script)");
    }
}

if (require.main === module) {
    main();
}

module.exports = { verifyCoinAuthenticity };
