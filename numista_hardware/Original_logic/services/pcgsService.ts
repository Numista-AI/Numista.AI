
import { Coin } from '../types';

interface PcgsCertResponse {
  Cert?: {
    PCGSNo: string;
    CertNo: string;
    Grade: string;
    Band?: string;
    Desig?: string;
  };
  PCGSNo?: string;
  CertNo?: string;
  Grade?: string;
  Band?: string;
  Desig?: string;
}

async function fetchWithProxy(url: string, options: any): Promise<Response> {
    const proxies = [
        { name: 'Corsproxy.io', fn: (u: string) => `https://corsproxy.io/?${encodeURIComponent(u)}` },
        { name: 'AllOrigins', fn: (u: string) => `https://api.allorigins.win/get?url=${encodeURIComponent(u)}` }
    ];

    let lastErrorDetail = "";

    if (options.method === 'POST') {
        try {
            const directResponse = await fetch(url, options);
            if (directResponse.ok || directResponse.status === 401) return directResponse;
        } catch (e) {}
        
        try {
            const proxyUrl = `https://corsproxy.io/?${encodeURIComponent(url)}`;
            const proxyResponse = await fetch(proxyUrl, options);
            if (proxyResponse.ok || proxyResponse.status === 401 || proxyResponse.status === 404) return proxyResponse;
        } catch (e) {}
    }

    for (const proxy of proxies) {
        try {
            const proxyUrl = proxy.fn(url);
            const response = await fetch(proxyUrl, { 
                ...options,
                headers: {
                    ...options.headers,
                    'Cache-Control': 'no-cache'
                }
            });

            if (proxy.name === 'AllOrigins') {
                const json = await response.json();
                if (json.contents) {
                    return new Response(json.contents, {
                        status: 200,
                        headers: { 'Content-Type': 'application/json' }
                    });
                }
            }

            if (response.ok || response.status === 401 || response.status === 404) {
                return response;
            }
            lastErrorDetail = `${proxy.name} status ${response.status}`;
        } catch (e: any) {
            lastErrorDetail = `${proxy.name} error: ${e.message}`;
            continue; 
        }
    }

    try {
        return await fetch(url, options);
    } catch (e: any) {
        throw new Error(`Connection to PCGS failed. ${lastErrorDetail}`);
    }
}

export const loginToPcgs = async (username: string, password: string): Promise<string> => {
    const authEndpoints = [
        "https://api.pcgs.com/oauth/token",
        "https://api.pcgs.com/publicapi/oauth/token"
    ];
    
    const body = new URLSearchParams();
    body.append('grant_type', 'password');
    body.append('username', username);
    body.append('password', password);

    let lastStatus = 0;
    let lastError = "";

    for (const authUrl of authEndpoints) {
        try {
            const response = await fetchWithProxy(authUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json'
                },
                body: body.toString()
            });

            lastStatus = response.status;

            if (response.ok) {
                const data = await response.json();
                if (data.access_token) return data.access_token;
            } else if (response.status === 401 || response.status === 400) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.error_description || "Invalid PCGS credentials.");
            }
        } catch (error: any) {
            if (error.message.includes("credentials")) throw error;
            lastError = error.message;
            console.warn(`PCGS auth trial failed at ${authUrl}:`, error.message);
        }
    }

    throw new Error(`PCGS Login failed (Status: ${lastStatus}). ${lastError || "Check your credentials or account permissions."}`);
};

export const fetchPcgsCertDetails = async (certNumber: string, apiToken: string): Promise<Partial<Coin> | null> => {
  if (!certNumber || !apiToken) return null;
  
  const cleanCert = certNumber.replace(/[^0-9]/g, '');
  if (!cleanCert) throw new Error("Invalid Certificate Number.");

  const endpoints = [
    `https://api.pcgs.com/publicapi/v1/Cert/GetByCertNo?certNo=${cleanCert}`,
    `https://api.pcgs.com/publicapi/v1/cert/getbycertno?certNo=${cleanCert}`,
    `https://api.pcgs.com/publicapi/v1/Cert/Verify/${cleanCert}`
  ];

  let lastStatus = 0;

  for (const url of endpoints) {
    try {
        const headers = {
            'Authorization': `Bearer ${apiToken}`,
            'Accept': 'application/json'
        };

        const response = await fetchWithProxy(url, { method: 'GET', headers });
        lastStatus = response.status;

        if (response.status === 401) {
            throw new Error("Unauthorized: Your PCGS session has expired or the token is invalid.");
        }

        if (response.ok) {
            const rawData: PcgsCertResponse = await response.json();
            const data = rawData.Cert || rawData;
            
            if (data && (data.Grade || data.CertNo)) {
                const fullGrade = [data.Grade, data.Band, data.Desig].filter(Boolean).join(' ');

                // Fixed: Replaced 'description' with 'personalNotes' as 'description' is not a valid property of Coin
                return {
                    certification: {
                        service: 'PCGS',
                        serialNumber: data.CertNo || cleanCert,
                        grade: fullGrade || 'Unknown'
                    },
                    personalNotes: data.PCGSNo ? `PCGS Coin #${data.PCGSNo}.` : `Verified PCGS Cert #${cleanCert}.`
                };
            }
        }
    } catch (error: any) {
        if (error.message.includes("Unauthorized")) throw error;
        console.warn(`PCGS path trial failed (${url}):`, error.message);
    }
  }

  if (lastStatus === 404) {
      throw new Error(`PCGS 404: Cert #${cleanCert} not found in the Public API. Ensure your account has 'Public API' access enabled.`);
  }

  throw new Error(`Failed to retrieve Cert #${cleanCert}. (Status: ${lastStatus}). Please verify your token permissions on the PCGS developer portal.`);
};
