/**
 * import_excel.js
 * 
 * Imports coin data from an Excel file, cleans it using AI, and saves to Firestore.
 * Usage: node import_excel.js <path-to-excel-file>
 */

const XLSX = require('xlsx');
const admin = require('firebase-admin');
const { mapToSchema } = require('./mappingController');
const path = require('path');

// Initialize Firebase Admin (Assumes ADC or Service Account)
// For local dev with 'firebase login', this often works if env vars are set, 
// otherwise explicit service account key might be needed. 
// For this environment, we'll try default app.
try {
    admin.initializeApp({
        projectId: 'studio-9101802118-8c9a8'
    });
} catch (e) {
    // Already initialized
}

const db = admin.firestore();
const COLLECTION_NAME = 'coins';

async function importExcel(filePath) {
    console.log(`Reading file: ${filePath}`);

    let workbook;
    try {
        workbook = XLSX.readFile(filePath);
    } catch (error) {
        console.error("Error reading file:", error.message);
        process.exit(1);
    }

    const sheetName = workbook.SheetNames[0];
    const sheet = workbook.Sheets[sheetName];
    const rawData = XLSX.utils.sheet_to_json(sheet);

    console.log(`Found ${rawData.length} rows. Starting processing...`);

    const batchSize = 400; // Firestore batch limit is 500
    let batch = db.batch();
    let count = 0;
    let totalProcessed = 0;

    for (const row of rawData) {
        // 1. Map & Clean (Gemini 3)
        process.stdout.write(`Processing row ${totalProcessed + 1}... `);

        try {
            const cleanedData = await mapToSchema(row);

            // 2. Add Metadata
            cleanedData.created_at = admin.firestore.FieldValue.serverTimestamp();
            cleanedData.deep_dive_status = 'PENDING';

            // 3. Queue for Batch Write
            const docRef = db.collection(COLLECTION_NAME).doc(); // Auto-ID
            cleanedData.id = docRef.id;

            batch.set(docRef, cleanedData);
            process.stdout.write("Done.\n");

            count++;
            totalProcessed++;
        } catch (err) {
            process.stdout.write("Failed (Skipping).\n");
            console.error(err);
        }

        // Commit batch if full
        if (count >= batchSize) {
            console.log("Committing batch...");
            await batch.commit();
            batch = db.batch();
            count = 0;
        }
    }

    // Commit remaining
    if (count > 0) {
        console.log("Committing final batch...");
        await batch.commit();
    }

    console.log(`\nSuccess! Imported ${totalProcessed} coins into '${COLLECTION_NAME}'.`);
}

// CLI Argument Handling
const args = process.argv.slice(2);
if (args.length !== 1) {
    console.log("Usage: node import_excel.js <path-to-excel-file>");
    process.exit(1);
}

importExcel(args[0]);
