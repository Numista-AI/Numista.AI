
const BASE_URL = 'https://api.numista.com/api/v2';

export interface NumistaCoinSearch {
  id: number;
  title: string;
  issuer: { name: string };
  min_year: number;
  max_year: number;
}

export interface NumistaCoinDetail {
  id: number;
  title: string;
  weight?: number;
  diameter?: number;
  thickness?: number;
  shape?: string;
  composition?: { text: string };
  mintage?: Array<{ year: string; mintage: number; note?: string }>;
}

export const searchNumista = async (query: string, apiKey: string): Promise<NumistaCoinSearch[]> => {
  try {
    const url = `${BASE_URL}/coins?q=${encodeURIComponent(query)}`;
    const response = await fetch(url, {
      headers: {
        'Numista-API-Key': apiKey,
        'Accept': 'application/json'
      }
    });

    if (!response.ok) {
       if (response.status === 401 || response.status === 403) {
           throw new Error("Invalid Numista API Key");
       }
       throw new Error(`Numista API Error: ${response.status}`);
    }

    const data = await response.json();
    return data.coins || [];
  } catch (error) {
    console.error("Numista search failed:", error);
    throw error;
  }
};

export const getNumistaCoinDetails = async (coinId: number, apiKey: string): Promise<NumistaCoinDetail> => {
  try {
    const url = `${BASE_URL}/coins/${coinId}`;
    const response = await fetch(url, {
      headers: {
        'Numista-API-Key': apiKey,
        'Accept': 'application/json'
      }
    });

    if (!response.ok) {
       throw new Error(`Numista Details Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Numista details failed:", error);
    throw error;
  }
};
