const { onRequest } = require("firebase-functions/v2/https");
const { onDocumentCreated } = require("firebase-functions/v2/firestore");
const logger = require("firebase-functions/logger");
const admin = require("firebase-admin");
const app = require("./server");

// Initialize Firebase Admin (safe to call multiple times)
if (!admin.apps.length) {
  admin.initializeApp();
}

// ── Existing HTTP function ────────────────────────────────────────────────────
exports.app = onRequest({ region: "us-west1", minInstances: 0 }, app);

// ── Feedback Intelligence trigger ────────────────────────────────────────────
// Fires within seconds of every new beta_feedback document being created.
// Pipeline: Gemini analysis → enrich Firestore doc → email alert → monthly rollup
const {
  analyzeWithGemini,
  sendAlertEmail,
  updateInsights,
  enrichFeedbackDoc,
} = require("./feedbackIntelligence");

exports.onFeedbackCreated = onDocumentCreated(
  {
    document: "beta_feedback/{docId}",
    region: "us-central1",
    secrets: ["NUMISTA_GMAIL_APP_PASSWORD"],
    timeoutSeconds: 120,
    memory: "512MiB",
  },
  async (event) => {
    const snap = event.data;
    if (!snap) {
      logger.warn("onFeedbackCreated: no snapshot data");
      return;
    }

    const doc = snap.data();
    const docId = event.params.docId;
    logger.info(`onFeedbackCreated: processing ${docId} type=${doc.issue_type}`);

    try {
      // 1. Gemini analysis (parallel-safe — reads only)
      const analysis = await analyzeWithGemini(doc);
      logger.info(`Analysis complete for ${docId}`, { tags: analysis.pattern_tags });

      // 2-4. Write back, send email, update rollup (in parallel)
      await Promise.allSettled([
        enrichFeedbackDoc(docId, analysis),
        sendAlertEmail(doc, analysis),
        updateInsights(doc, analysis),
      ]);

      logger.info(`onFeedbackCreated: complete for ${docId}`);
    } catch (err) {
      logger.error(`onFeedbackCreated: unhandled error for ${docId}`, err);
    }
  }
);
