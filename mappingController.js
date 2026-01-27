const genaiPackage = require('@google/genai');
const GoogleGenAI = genaiPackage.GoogleGenAI;
const fs = require('fs');
const path = require('path');
require('dotenv').config();

console.log('MappingController: GoogleGenAI type:', typeof GoogleGenAI);

// 1. Load and clean the schema
const schemaPath = path.join(__dirname, 'coin-schema.json');
let rawSchema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
delete rawSchema.$schema;
delete rawSchema.title;

const COIN_DICTIONARY = [
    { "val": 0.01, "formal": "Lincoln Cent", "slang": ["penny", "wheatie", "steelie", "red cent"] },
    { "val": 0.05, "formal": "Jefferson Nickel", "slang": ["nickel", "buffalo", "war nickel", "v-nickel"] },
    { "val": 0.10, "formal": "Roosevelt Dime", "slang": ["dime", "mercury", "rosie", "winged liberty"] },
    { "val": 0.25, "formal": "Washington Quarter", "slang": ["quarter", "two bits", "state quarter", "2026 semiquin"] },
    { "val": 0.50, "formal": "Kennedy Half Dollar", "slang": ["half", "fifty cent", "franklin", "walker"] },
    { "val": 1.00, "formal": "Morgan Silver Dollar", "slang": ["morgan", "silver dollar", "cartwheel", "peace dollar"] }
];

// 3. Define the Model
// Using 'gemini-3-flash-preview' as requested.
const modelId = 'gemini-3-flash-preview';

async function mapToSchema(entities) {
    // Lazy Initialization
    const apiKey = process.env.GOOGLE_API_KEY;
    if (!apiKey) {
        throw new Error("❌ MISSING API KEY: Please set GOOGLE_API_KEY in your .env file.");
    }
    console.log("Initialize GenAI with Key length:", apiKey.length);
    const genai = new GoogleGenAI({ apiKey: apiKey });

    const prompt = `Convert these entities into the 21-column schema.
    Use this dictionary to map slang to formal coin names: ${JSON.stringify(COIN_DICTIONARY)}
    Entities: ${JSON.stringify(entities)}`;

    try {
        const result = await genai.models.generateContent({
            model: modelId,
            config: {
                responseMimeType: 'application/json',
                responseSchema: rawSchema
            },
            contents: [{ parts: [{ text: prompt }] }]
        });

        console.log("Result Keys:", Object.keys(result));

        let responseText;
        if (result.candidates && result.candidates.length > 0) {
            const part = result.candidates[0].content.parts[0];
            responseText = part.text;
        } else {
            console.warn("No candidates found, dumping result string.");
            responseText = JSON.stringify(result);
        }
        return JSON.parse(responseText);

    } catch (error) {
        console.error("❌ Gemini Mapping Error:", error);
        throw error;
    }
}

module.exports = { mapToSchema };