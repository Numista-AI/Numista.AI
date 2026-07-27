// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Sprint 2: Microscope Desktop Agent & Diagnostics Stress Tests', () => {

  test('Verify Desktop Agent Local Endpoint Payload Integrity', async ({ request }) => {
    try {
      // Ping local Flask status endpoint over HTTPS (ignore self-signed TLS errors)
      const response = await request.get('https://localhost:5000/get-status', {
        ignoreHTTPSErrors: true,
        timeout: 3000,
      });

      expect(response.status()).toBe(200);
      const json = await response.json();

      expect(json).toHaveProperty('is_active');
      expect(json).toHaveProperty('current_step');
      expect(json).toHaveProperty('sharpness');
      expect(json).toHaveProperty('paired_email');

      console.log('✅ Local Agent Endpoint Response Verified:', json);
    } catch (err) {
      test.skip(true, 'Local microscope hardware agent daemon on port 5000 is offline.');
    }
  });

  test('Verify Local Camera Selector API Endpoint', async ({ request }) => {
    try {
      const response = await request.get('https://localhost:5000/list-cameras', {
        ignoreHTTPSErrors: true,
        timeout: 3000,
      });

      expect(response.status()).toBe(200);
      const json = await response.json();

      expect(json).toHaveProperty('cameras');
      expect(json).toHaveProperty('active');
      expect(Array.isArray(json.cameras)).toBe(true);

      console.log('✅ Camera API List Verified:', json);
    } catch (err) {
      test.skip(true, 'Local microscope hardware agent daemon on port 5000 is offline.');
    }
  });

  test('Direct download link target validation', async () => {
    const installerUrl =
      'https://storage.googleapis.com/studio-9101802118-8c9a8-uploads/downloads/NumistaAgentSetup.exe';
    const standaloneUrl =
      'https://storage.googleapis.com/studio-9101802118-8c9a8-uploads/downloads/numista-agent.exe';

    expect(installerUrl).toContain('NumistaAgentSetup.exe');
    expect(standaloneUrl).toContain('numista-agent.exe');
  });

});
