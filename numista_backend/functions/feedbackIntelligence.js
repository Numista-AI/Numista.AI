/**
 * feedbackIntelligence.js
 * Heavy imports are lazy-loaded inside function bodies to avoid
 * Firebase CLI deployment analysis timeout.
 */

const admin = require("firebase-admin");
const logger = require("firebase-functions/logger");
const { buildEmailHtml } = require("./emailTemplate");

const PROJECT_ID  = "studio-9101802118-8c9a8";
const ALERT_TO    = "eric@numista.ai";
const ALERT_FROM  = "eric@numista.ai";
const SECRET_NAME = `projects/${PROJECT_ID}/secrets/NUMISTA_GMAIL_APP_PASSWORD/versions/latest`;

let _cachedPassword = null;

async function getGmailPassword() {
  if (_cachedPassword) return _cachedPassword;
  // Lazy-load to avoid startup timeout
  const { SecretManagerServiceClient } = require("@google-cloud/secret-manager");
  const client = new SecretManagerServiceClient();
  const [version] = await client.accessSecretVersion({ name: SECRET_NAME });
  _cachedPassword = version.payload.data.toString("utf8").trim();
  return _cachedPassword;
}

// ── 1. Gemini analysis ────────────────────────────────────────────────────────

async function analyzeWithGemini(doc) {
  try {
    // Lazy-load to avoid startup timeout
    const { GoogleGenAI } = require("@google/genai");
    const ai = new GoogleGenAI({ apiKey: process.env.GOOGLE_API_KEY });

    const transcript = (doc.full_transcript || [])
      .map(m => `${m.role === "user" ? "USER" : "MORGAN"}: ${m.message || m.message_redacted || ""}`)
      .join("\n");

    const prompt = `You are a senior product engineer and triage assistant for Numista.AI,
a Flutter web app for coin collectors. A beta user just submitted feedback via the MORGAN interview system.

Feedback document:
- Issue type: ${doc.issue_type}
- Severity estimate: ${doc.severity_estimate}
- Affected feature: ${doc.affected_feature || "unknown"}
- MORGAN summary: ${doc.morgan_summary || "none"}
- User confirmed text: ${doc.morgan_summary_confirmed_text || "none"}
- Intake method: ${doc.intake_method}
- Interview turns: ${doc.interview_turns}
- Page/Route: ${doc.page_title} (${doc.route})
- Transcript:
${transcript.substring(0, 3000)}

Analyze this feedback and return ONLY valid JSON (no markdown, no explanation):
{
  "root_cause_hypothesis": "one concise sentence explaining the likely technical root cause",
  "suggested_fix_area": "specific file/component/line if identifiable, e.g. feedback_fallback_form.dart ~line 172",
  "priority_rationale": "one sentence on why this matters and who it affects",
  "pattern_tags": ["array", "of", "short", "keyword", "tags"],
  "estimated_effort": "small",
  "related_screens": ["screen_name"],
  "engineering_notes": "optional 1-2 sentences of additional context for the engineer addressing this"
}

estimated_effort must be exactly one of: small, medium, large
pattern_tags should be 2-5 lowercase keywords (e.g. "overlay", "web-only", "auth", "navigation", "performance")`;

    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash-preview-05-20",
      contents: [{ role: "user", parts: [{ text: prompt }] }],
    });

    const raw = response.candidates?.[0]?.content?.parts?.[0]?.text || "{}";
    const cleaned = raw.replace(/^```json\s*/i, "").replace(/```\s*$/, "").trim();
    return JSON.parse(cleaned);
  } catch (err) {
    logger.error("Gemini analysis failed", err);
    return {
      root_cause_hypothesis: "Analysis unavailable",
      suggested_fix_area: "—",
      priority_rationale: "Manual review required",
      pattern_tags: [],
      estimated_effort: "medium",
      related_screens: [],
      engineering_notes: "",
    };
  }
}

// ── 2. Send Gmail alert ───────────────────────────────────────────────────────

async function sendAlertEmail(doc, analysis) {
  // Lazy-load nodemailer to avoid startup timeout
  const nodemailer = require("nodemailer");
  const password = await getGmailPassword();

  const transporter = nodemailer.createTransport({
    service: "gmail",
    auth: { user: ALERT_FROM, pass: password },
  });

  const sev = doc.severity_estimate || "MEDIUM";
  const issueLabel = {
    BUG: "Bug Report", FEATURE: "Feature Request", UX: "UX/Design",
    PRAISE: "Praise", CONFUSION: "Confusing", OTHER: "Other",
  }[doc.issue_type] || doc.issue_type;

  const subject = `[${sev}] New Feedback: ${issueLabel} — ${doc.page_title || doc.route || "Numista.AI"}`;
  const html = buildEmailHtml(doc, analysis);

  await transporter.sendMail({
    from: `"Numista Feedback Bot" <${ALERT_FROM}>`,
    to: ALERT_TO,
    subject,
    html,
  });

  logger.info(`Alert email sent for doc ${doc.feedback_id}`);
}

// ── 3. Monthly insights rollup ────────────────────────────────────────────────

async function updateInsights(doc, analysis) {
  const db = admin.firestore();
  const now = new Date();
  const period = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
  const ref = db.collection("feedback_insights").doc(period);   // .doc() not .document()

  const FieldValue = admin.firestore.FieldValue;

  const update = {
    period,
    total_submissions: FieldValue.increment(1),
    last_updated: FieldValue.serverTimestamp(),
    [`by_issue_type.${doc.issue_type || "OTHER"}`]: FieldValue.increment(1),
    [`by_severity.${doc.severity_estimate || "MEDIUM"}`]: FieldValue.increment(1),
    [`by_intake_method.${doc.intake_method || "unknown"}`]: FieldValue.increment(1),
  };

  for (const tag of (analysis.pattern_tags || [])) {
    const safeTag = tag.replace(/[^a-zA-Z0-9_]/g, "_");
    update[`pattern_tag_frequency.${safeTag}`] = FieldValue.increment(1);
  }

  for (const screen of (analysis.related_screens || [])) {
    const safeScreen = screen.replace(/[^a-zA-Z0-9_]/g, "_");
    update[`affected_screens.${safeScreen}`] = FieldValue.increment(1);
  }

  await ref.set(update, { merge: true });
  logger.info(`Insights updated for period ${period}`);
}

// ── 4. Write ai_analysis back to the feedback doc ────────────────────────────

async function enrichFeedbackDoc(docId, analysis) {
  const db = admin.firestore();
  await db.collection("beta_feedback").doc(docId).update({   // .doc() not .document()
    ai_analysis: analysis,
    ai_analysis_ts: admin.firestore.FieldValue.serverTimestamp(),
  });
}

module.exports = { analyzeWithGemini, sendAlertEmail, updateInsights, enrichFeedbackDoc };
