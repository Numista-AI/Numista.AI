const pkg = require('@google/genai');
const { GoogleGenAI } = pkg;
try {
    const client = new GoogleGenAI({ apiKey: 'test' });
    console.log('Client keys:', Object.keys(client));
    if (client.models) {
        console.log('Client has .models');
        console.log('Models keys:', Object.keys(client.models));
    }
    if (client.languageModel) console.log('Client has .languageModel');
} catch (e) {
    console.error('Error:', e);
}
