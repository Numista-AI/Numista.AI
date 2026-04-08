
import { GoogleGenAI, Type } from "@google/genai";
import { Coin, Source } from "../types";

const parseJsonResponse = (text: string, defaultValue: any = {}) => {
  if (!text) return defaultValue;
  const cleaned = text.replace(/```json|```/g, '').trim();
  try {
    return JSON.parse(cleaned);
  } catch (e) {
    const startBracket = cleaned.indexOf('[');
    const endBracket = cleaned.lastIndexOf(']');
    if (startBracket !== -1 && endBracket !== -1) {
      try {
        return JSON.parse(cleaned.substring(startBracket, endBracket + 1));
      } catch (inner) {}
    }
    const firstObj = cleaned.indexOf('{');
    const lastObj = cleaned.lastIndexOf('}');
    if (firstObj !== -1 && lastObj !== -1) {
      try {
        return JSON.parse(cleaned.substring(firstObj, lastObj + 1));
      } catch (inner) {}
    }
    return defaultValue;
  }
};

export const estimateCoinValue = async (coin: Coin): Promise<ValuationResult> => {
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  const prompt = `Appraise this coin: ${coin.year} ${coin.country} ${coin.denomination}. Condition: ${coin.condition}. Provide estimated minimum and maximum retail values in USD, face value if applicable, and a brief market summary.`;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: prompt,
      config: {
        tools: [{ googleSearch: {} }],
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            minPrice: { type: Type.NUMBER },
            maxPrice: { type: Type.NUMBER },
            faceValue: { type: Type.NUMBER },
            summary: { type: Type.STRING }
          },
          required: ["minPrice", "maxPrice", "summary"]
        },
        temperature: 0.1,
      },
    });
    const data = parseJsonResponse(response.text || '{}');
    const sources: Source[] = [];
    response.candidates?.[0]?.groundingMetadata?.groundingChunks?.forEach((chunk) => {
      if (chunk.web) sources.push({ title: chunk.web.title || 'Market Source', uri: chunk.web.uri || '#' });
    });

    return {
      min: Number(data.minPrice) || 0,
      max: Number(data.maxPrice) || 0,
      faceValue: Number(data.faceValue) || 0,
      notes: data.summary || '',
      sources: sources
    };
  } catch (error) {
    console.error("Valuation failed:", error);
    throw new Error("Valuation failed.");
  }
};

export const processImportedData = async (rawData: any[], onProgress?: (current: number, total: number) => void): Promise<Coin[]> => {
  const CHUNK_SIZE = 10; 
  let allProcessed: Coin[] = [];

  for (let i = 0; i < rawData.length; i += CHUNK_SIZE) {
    const chunk = rawData.slice(i, i + CHUNK_SIZE);
    if (onProgress) onProgress(i, rawData.length);

    const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
    const prompt = `Map these raw spreadsheet rows to a standard JSON Coin object array. 
    Important Column Mappings:
    - 'Program/Series' -> series
    - 'Theme/Subject' -> theme
    - 'Surface & Strike Quality' -> surfaceQuality
    - 'Grading Service' -> certification.service
    - 'Grading Certification Number' -> certification.serialNumber
    - 'Cost' -> purchaseCost
    - 'Retailer/Website' -> retailer
    - 'Retailer Item No.' -> retailerItemNo
    - 'Retailer Invoice #' -> retailerInvoiceNo
    - 'Melt Value' -> meltValue
    - 'Personal Notes' -> personalNotes
    - 'Personal Reference #' -> personalRefNo
    - 'Storage Location' -> storageLocation
    - 'Variety (Legacy)' -> varietyLegacy
    - 'Notes (Legacy)' -> notesLegacy
    
    Data: ${JSON.stringify(chunk)}`;
    
    try {
      const response = await ai.models.generateContent({
        model: 'gemini-3-flash-preview',
        contents: prompt,
        config: { 
          responseMimeType: "application/json",
          thinkingConfig: { thinkingBudget: 0 }, 
          responseSchema: {
            type: Type.ARRAY,
            items: {
              type: Type.OBJECT,
              properties: {
                year: { type: Type.STRING },
                country: { type: Type.STRING },
                denomination: { type: Type.STRING },
                mintMark: { type: Type.STRING },
                condition: { type: Type.STRING },
                quantity: { type: Type.NUMBER },
                purchaseCost: { type: Type.NUMBER },
                series: { type: Type.STRING },
                theme: { type: Type.STRING },
                surfaceQuality: { type: Type.STRING },
                retailer: { type: Type.STRING },
                retailerItemNo: { type: Type.STRING },
                retailerInvoiceNo: { type: Type.STRING },
                meltValue: { type: Type.NUMBER },
                personalNotes: { type: Type.STRING },
                personalRefNo: { type: Type.STRING },
                storageLocation: { type: Type.STRING },
                varietyLegacy: { type: Type.STRING },
                notesLegacy: { type: Type.STRING },
                metalContent: { type: Type.STRING },
                certService: { type: Type.STRING },
                certSerial: { type: Type.STRING },
                datePurchased: { type: Type.STRING }
              }
            }
          }
        }
      });
      
      const normalized = parseJsonResponse(response.text || '[]', []);
      if (Array.isArray(normalized)) {
        const mapped = normalized.map((c: any) => ({
          ...c,
          id: crypto.randomUUID(),
          dateAdded: new Date().toISOString(),
          currency: 'USD',
          year: String(c.year || 'Unknown'),
          country: c.country || 'United States',
          denomination: c.denomination || 'Unknown',
          condition: c.condition || 'Circulated',
          quantity: Number(c.quantity) || 1,
          purchaseCost: Number(c.purchaseCost) || 0,
          certification: (c.certService || c.certSerial) ? {
            service: c.certService || '',
            serialNumber: c.certSerial || '',
            grade: c.condition || ''
          } : undefined
        }));
        allProcessed = [...allProcessed, ...mapped];
      }
    } catch (e) { console.error(e); }
  }

  if (onProgress) onProgress(rawData.length, rawData.length);
  return allProcessed;
};

export const generateCoinAnalysis = async (coin: Coin): Promise<{ text: string }> => {
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  const prompt = `Provide a professional numismatic analysis for a ${coin.year} ${coin.country} ${coin.denomination}. 
  Include historical background, production details, and key features for collectors. Use Markdown for formatting.`;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-pro-preview',
      contents: prompt,
      config: {
        thinkingConfig: { thinkingBudget: 4000 }
      }
    });
    return { text: response.text || "Failed to generate report." };
  } catch (error) {
    console.error("Analysis generation failed:", error);
    return { text: "Error generating analysis." };
  }
};

export const findMissingCoinsForSet = async (setName: string, selectedCoins: Coin[], availableCoins: Coin[]): Promise<string[]> => {
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  const prompt = `Task: Find which available coins belong in the set "${setName}". 
  Set currently contains: ${selectedCoins.map(c => `${c.year} ${c.denomination}`).join(', ')}.
  Check these candidates: ${JSON.stringify(availableCoins.map(c => ({ id: c.id, y: c.year, d: c.denomination, s: c.series })))}.
  Return ONLY a JSON array of string IDs.`;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.ARRAY,
          items: { type: Type.STRING }
        }
      }
    });
    return parseJsonResponse(response.text || '[]', []);
  } catch (error) {
    console.error("Set scan failed:", error);
    return [];
  }
};

export const getCollectionInsights = async (coins: Coin[], query: string): Promise<string> => {
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  const coinSummary = coins.slice(0, 10).map(c => ({ y: c.year, d: c.denomination, v: c.estimatedValueMax }));
  const prompt = `As a numismatic expert, analyze this subset of the user's collection: ${JSON.stringify(coinSummary)}. 
  Answer the user's query: "${query}"`;
  
  try {
    const response = await ai.models.generateContent({ 
        model: 'gemini-3-flash-preview', 
        contents: prompt,
        config: { thinkingConfig: { thinkingBudget: 0 } }
    });
    return response.text || "No insights available at this time.";
  } catch (e) { 
    console.error("Insights error:", e);
    return "I'm having trouble analyzing your collection right now."; 
  }
};

interface ValuationResult {
  min: number;
  max: number;
  faceValue?: number;
  notes: string;
  sources: Source[];
}
