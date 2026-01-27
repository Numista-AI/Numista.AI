
import { GoogleGenAI } from "@google/genai";

export interface NgcVerificationResult {
  isValid: boolean;
  gradeMatches: boolean;
  coinDescription: string;
  population?: number;
  censusUrl?: string;
  notes?: string;
}

/**
 * Clean and parse JSON from Gemini response which may be wrapped in markdown blocks
 */
const parseJsonResponse = (text: string, defaultValue: any = {}) => {
  try {
    // Try direct parse first
    return JSON.parse(text);
  } catch (e) {
    // Strip potential markdown code blocks
    const cleanText = text
      .replace(/^```json\n?/, '')
      .replace(/\n?```$/, '')
      .trim();
    try {
      return JSON.parse(cleanText);
    } catch (innerError) {
      console.error("JSON Parse Error in NGC service. Raw text:", text);
      return defaultValue;
    }
  }
};

/**
 * Verifies an NGC Certificate using AI Search Grounding.
 */
export const verifyNgcCert = async (certNumber: string, grade: string): Promise<NgcVerificationResult> => {
  // Fix: Initialize AI client inside function to ensure it uses the latest API key
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  const prompt = `
    Task: Verify an NGC Coin Certificate.
    
    Cert Number: "${certNumber}"
    Claimed Grade: "${grade}"
    
    1. Search for "NGC Coin Certificate Verification ${certNumber}".
    2. Extract the coin details from the search results (Year, Denomination, Variety).
    3. Verify if the grade in the search result matches "${grade}".
    4. Look for "Total Graded" or "Population" figures if available in snippets.
    
    Return JSON:
    {
      "isValid": boolean,
      "gradeMatches": boolean,
      "coinDescription": string,
      "population": number,
      "notes": string
    }
  `;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: prompt,
      config: {
        tools: [{ googleSearch: {} }],
        responseMimeType: "application/json",
        temperature: 0,
      }
    });

    const data = parseJsonResponse(response.text || '{}');

    return {
      isValid: data.isValid || false,
      gradeMatches: data.gradeMatches || false,
      coinDescription: data.coinDescription || 'Details not found',
      population: data.population,
      notes: data.notes
    };
  } catch (error) {
    console.error("NGC Verification Failed:", error);
    throw new Error("Unable to verify NGC cert at this time.");
  }
};

/**
 * Generates the URL for the NGC Census/Population report.
 */
export const getNgcPopulationReportUrl = (certNumber: string) => {
    const cleanCert = certNumber.split('-')[0];
    return `https://www.ngccoin.com/certlookup/${cleanCert}/`;
};
