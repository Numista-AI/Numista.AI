const test = require("node:test");
const assert = require("node:assert/strict");
const Module = require("node:module");
const path = require("node:path");

function makeFetchRecorder(captured) {
  return async (url, init = {}) => {
    const headers = {};
    if (init.headers) {
      if (typeof init.headers.forEach === "function") {
        init.headers.forEach((v, k) => {
          headers[String(k).toLowerCase()] = String(v);
        });
      } else {
        for (const [k, v] of Object.entries(init.headers)) {
          headers[String(k).toLowerCase()] = String(v);
        }
      }
    }
    const body = typeof init.body === "string" ? JSON.parse(init.body) : null;
    captured.push({
      url: String(url),
      method: String(init.method || "GET").toUpperCase(),
      headers,
      body,
    });
    return new Response(
      JSON.stringify({
        candidates: [
          {
            content: {
              role: "model",
              parts: [
                {
                  text: JSON.stringify({
                    root_cause_hypothesis: "ok",
                    suggested_fix_area: "ui",
                    priority_rationale: "low",
                    pattern_tags: ["ui"],
                    estimated_effort: "small",
                    related_screens: ["home"],
                    engineering_notes: "none",
                  }),
                },
              ],
            },
          },
        ],
      }),
      { status: 200, headers: { "content-type": "application/json" } }
    );
  };
}

function assertHydrogenRequest(req) {
  assert.equal(req.method, "POST");
  assert.match(req.url, /\/models\/gemini-4-hydrogen:generateContent$/);
  const apiKey = req.headers["x-goog-api-key"];
  assert.ok(apiKey && apiKey.length > 5, "x-goog-api-key header must be present");
  assert.ok(req.body && req.body.generationConfig, "generationConfig must be present");
  assert.equal(req.body.generationConfig.thinkingConfig?.thinkingLevel?.toLowerCase(), "low");
  assert.equal(req.body.generationConfig.temperature, undefined);
  assert.equal(req.body.generationConfig.topP, undefined);
  assert.equal(req.body.generationConfig.topK, undefined);
  assert.equal(req.body.generationConfig.thinkingConfig?.thinkingBudget, undefined);
  assert.equal(req.body.cachedContent, undefined);
}

function withStubbedRequire(stubs, fn) {
  const origLoad = Module._load;
  Module._load = function (request, parent, isMain) {
    if (Object.prototype.hasOwnProperty.call(stubs, request)) {
      return stubs[request];
    }
    return origLoad.apply(this, arguments);
  };
  return Promise.resolve()
    .then(fn)
    .finally(() => {
      Module._load = origLoad;
    });
}

test("functions/mappingController.js sends Hydrogen P5 request", async () => {
  const captured = [];
  const origFetch = globalThis.fetch;
  const origKey = process.env.GOOGLE_API_KEY;
  globalThis.fetch = makeFetchRecorder(captured);
  process.env.GOOGLE_API_KEY = "synthetic-node-test-key";
  try {
    const modPath = path.resolve(__dirname, "../mappingController.js");
    delete require.cache[modPath];
    const { mapToSchema } = require(modPath);
    await mapToSchema(["1909-S VDB"]);
    assert.equal(captured.length, 1);
    assertHydrogenRequest(captured[0]);
  } finally {
    globalThis.fetch = origFetch;
    if (origKey === undefined) delete process.env.GOOGLE_API_KEY;
    else process.env.GOOGLE_API_KEY = origKey;
  }
});

test("root mappingController.js sends Hydrogen P5 request", async () => {
  const captured = [];
  const origFetch = globalThis.fetch;
  const origKey = process.env.GOOGLE_API_KEY;
  globalThis.fetch = makeFetchRecorder(captured);
  process.env.GOOGLE_API_KEY = "synthetic-node-test-key";
  try {
    const modPath = path.resolve(__dirname, "../../mappingController.js");
    delete require.cache[modPath];
    const { mapToSchema } = require(modPath);
    await mapToSchema(["1916-D"]);
    assert.equal(captured.length, 1);
    assertHydrogenRequest(captured[0]);
  } finally {
    globalThis.fetch = origFetch;
    if (origKey === undefined) delete process.env.GOOGLE_API_KEY;
    else process.env.GOOGLE_API_KEY = origKey;
  }
});

test("integration_service.js sends Hydrogen P5 request", async () => {
  const captured = [];
  const origFetch = globalThis.fetch;
  const origKey = process.env.GOOGLE_API_KEY;
  globalThis.fetch = makeFetchRecorder(captured);
  process.env.GOOGLE_API_KEY = "synthetic-node-test-key";
  try {
    await withStubbedRequire(
      {
        "firebase-admin": { initializeApp: () => {}, firestore: () => ({}) },
        "./invoiceService": { processInvoice: async () => ({}) },
      },
      async () => {
        const modPath = path.resolve(__dirname, "../../integration_service.js");
        delete require.cache[modPath];
        const { verifyCoinAuthenticity } = require(modPath);
        await verifyCoinAuthenticity("1909-S VDB Lincoln Cent", null);
      }
    );
    assert.equal(captured.length, 1);
    assertHydrogenRequest(captured[0]);
  } finally {
    globalThis.fetch = origFetch;
    if (origKey === undefined) delete process.env.GOOGLE_API_KEY;
    else process.env.GOOGLE_API_KEY = origKey;
  }
});

test("functions/feedbackIntelligence.js sends Hydrogen P5 request and guards missing key", async () => {
  const captured = [];
  const origFetch = globalThis.fetch;
  const origKey = process.env.GOOGLE_API_KEY;
  const origModel = process.env.GEMINI_FLASH_MODEL;
  globalThis.fetch = makeFetchRecorder(captured);
  const stubs = {
    "firebase-admin": {
      initializeApp: () => {},
      firestore: Object.assign(() => ({}), {
        FieldValue: { increment: () => ({}), serverTimestamp: () => ({}) },
      }),
    },
    "firebase-functions/logger": { info: () => {}, warn: () => {}, error: () => {} },
    nodemailer: { createTransport: () => ({ sendMail: async () => {} }) },
  };
  try {
    const modPath = path.resolve(__dirname, "../feedbackIntelligence.js");
    // Negative case: missing key -> 0 fetches
    delete process.env.GOOGLE_API_KEY;
    await withStubbedRequire(stubs, async () => {
      delete require.cache[modPath];
      const { analyzeWithGemini } = require(modPath);
      const fallback = await analyzeWithGemini({
        category: "bug",
        raw_text: "Button misaligned",
        route_context: "/home",
        platform: "web",
      });
      assert.equal(captured.length, 0);
      assert.equal(fallback.root_cause_hypothesis, "Analysis unavailable");
    });

    // Positive case with synthetic key
    process.env.GOOGLE_API_KEY = "synthetic-node-test-key";
    process.env.GEMINI_FLASH_MODEL = "gemini-4-hydrogen";
    await withStubbedRequire(stubs, async () => {
      delete require.cache[modPath];
      const { analyzeWithGemini } = require(modPath);
      await analyzeWithGemini({
        category: "bug",
        raw_text: "Button misaligned",
        route_context: "/home",
        platform: "web",
      });
      assert.equal(captured.length, 1);
      assertHydrogenRequest(captured[0]);
    });
  } finally {
    globalThis.fetch = origFetch;
    if (origKey === undefined) delete process.env.GOOGLE_API_KEY;
    else process.env.GOOGLE_API_KEY = origKey;
    if (origModel === undefined) delete process.env.GEMINI_FLASH_MODEL;
    else process.env.GEMINI_FLASH_MODEL = origModel;
  }
});
