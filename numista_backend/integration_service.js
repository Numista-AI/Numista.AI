/**
 * integration_service.js
 * 
 * Main integration entry point.
 * Examples of capabilities:
 * 1. Verify coin authenticity using Vertex AI.
 * 2. Process an Invoice PDF using Document AI.
 */

const { VertexAI } = require('@google-cloud/vertexai');
const admin = require('firebase-admin');
const { processInvoice } = require('./invoiceService');
const fs = require('fs');

// Initialize Configuration
const PROJECT_ID = 'studio-9101802118-8c9a8';
const LOCATION = 'us-central1';
const MODEL_NAME = 'gemini-1.5-flash-001';

// Initialize Firebase
try {
    admin.initializeApp({
        projectId: PROJECT_ID
    });
} catch (e) { }
const db = admin.firestore();

// Initialize Vertex AI
const vertexAI = new VertexAI({ project: PROJECT_ID, location: LOCATION });
const model = vertexAI.getGenerativeModel({ model: MODEL_NAME });

/**
 * Verifies coin authenticity using Vertex AI (Gemini).
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
        const result = await model.generateContent({
            contents: [{ role: 'user', parts }]
        });
        const response = result.response;
        const text = response.candidates[0].content.parts[0].text;

        console.log("--- Vertex AI Analysis ---");
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
