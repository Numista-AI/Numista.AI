const { DocumentProcessorServiceClient } = require('@google-cloud/documentai').v1;

const client = new DocumentProcessorServiceClient({
    keyFilename: './serviceAccountKey.json.json'
});

async function listProcessors() {
    console.log("Listing processors...");
    const parent = `projects/studio-9101802118-8c9a8/locations/us`;
    try {
        const [processors] = await client.listProcessors({ parent });
        console.log("Processors found:", processors.length);
        processors.forEach(p => console.log(` - ${p.displayName} (${p.state})`));
    } catch (error) {
        console.error("❌ List Processors Failed:", error);
    }
}

listProcessors();
