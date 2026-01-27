/**
 * invoiceService.js
 * 
 * Handles extracting line items from coin invoices using Google Cloud Document AI.
 */

const { DocumentProcessorServiceClient } = require('@google-cloud/documentai').v1;

// Configuration
const PROJECT_ID = 'studio-9101802118-8c9a8'; // Using the ID from your other files
const LOCATION = 'us'; // Default location for Document AI processors
const PROCESSOR_ID = 'c113e9bb62be1554';

// Initialize Client
const client = new DocumentProcessorServiceClient({
    keyFilename: './serviceAccountKey.json.json'
});

/**
 * Processes a PDF invoice and extracts entities.
 * @param {Buffer} fileBuffer - The PDF file as a buffer.
 * @returns {Promise<Array>} - Extracted entities.
 */
async function processInvoice(fileBuffer) {
    // 1. Construct the resource name
    const name = `projects/${PROJECT_ID}/locations/${LOCATION}/processors/${PROCESSOR_ID}`;

    // 2. Configure the request
    const request = {
        name,
        rawDocument: {
            content: fileBuffer,
            mimeType: 'application/pdf',
        },
    };

    try {
        // 3. Process the document
        const [result] = await client.processDocument(request);
        const { document } = result;

        console.log(`Document processing complete. Extracted ${document.entities.length} entities.`);

        // Return the entities found by the processor
        return document.entities;

    } catch (error) {
        console.error('Error processing invoice:', error);
        throw error;
    }
}

module.exports = { processInvoice };
