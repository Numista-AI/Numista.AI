const { mapToSchema } = require('./mappingController');

async function testGemini() {
    console.log("🧠 Testing Gemini 3 Flash Preview...");

    // Mock data mimicking Document AI output
    const mockEntities = [
        { type: 'item', mentionText: '1921 Morgan Silver Dollar' },
        { type: 'price', mentionText: '$100.00' }
    ];

    try {
        const result = await mapToSchema(mockEntities);
        console.log("✨ Gemini Mapping Success!");
        console.log(JSON.stringify(result, null, 2));
    } catch (error) {
        console.error("❌ Gemini Test Failed:", error);
        if (error.stack) console.error(error.stack);
    }
}

testGemini();
