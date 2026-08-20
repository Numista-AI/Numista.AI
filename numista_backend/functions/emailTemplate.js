/**
 * emailTemplate.js — HTML email builder for MORGAN feedback alerts.
 * Styled dark-theme email matching the Numista.AI aesthetic.
 */

const SEVERITY_CONFIG = {
  HIGH:     { emoji: '🔴', label: 'HIGH',     hex: '#EF4444' },
  CRITICAL: { emoji: '🚨', label: 'CRITICAL', hex: '#DC2626' },
  MEDIUM:   { emoji: '🟡', label: 'MEDIUM',   hex: '#F59E0B' },
  LOW:      { emoji: '🟢', label: 'LOW',      hex: '#22C55E' },
};

const ISSUE_LABELS = {
  BUG:       'Bug Report',
  FEATURE:   'Feature Request',
  UX:        'UX / Design',
  PRAISE:    'Praise',
  CONFUSION: 'Confusing / Hard to Use',
  OTHER:     'Other',
};

function buildEmailHtml(doc, analysis) {
  const sev = SEVERITY_CONFIG[doc.severity_estimate] || SEVERITY_CONFIG.MEDIUM;
  const issueLabel = ISSUE_LABELS[doc.issue_type] || doc.issue_type || 'Unknown';
  const method = doc.intake_method === 'morgan_interview' ? '🎙️ MORGAN Interview' : '📝 Fallback Form';
  const screenshotBlock = doc.screenshot_url
    ? `<p style="margin:8px 0"><a href="${doc.screenshot_url}" style="color:#60A5FA">📷 View Screenshot →</a></p>`
    : '<p style="color:#6B7280;margin:8px 0;font-size:13px">No screenshot attached</p>';

  const tagChips = (analysis.pattern_tags || []).map(t =>
    `<span style="background:#1E3A5F;color:#93C5FD;padding:2px 8px;border-radius:12px;font-size:12px;margin-right:4px">${t}</span>`
  ).join('');

  const effortColors = { small: '#22C55E', medium: '#F59E0B', large: '#EF4444' };
  const effortHex = effortColors[analysis.estimated_effort] || '#6B7280';

  const transcriptRows = (doc.full_transcript || []).slice(0, 8).map(m => {
    const isUser = m.role === 'user';
    const bg = isUser ? '#1E293B' : '#0F172A';
    const label = isUser ? '👤 User' : '🤖 MORGAN';
    const text = m.message || m.message_redacted || '';
    return `<tr><td style="background:${bg};padding:8px 12px;border-bottom:1px solid #1E293B;font-size:13px;color:${isUser ? '#E2E8F0' : '#94A3B8'}"><strong style="color:${isUser ? '#60A5FA' : '#818CF8'}">${label}:</strong> ${text.substring(0, 300)}${text.length > 300 ? '…' : ''}</td></tr>`;
  }).join('');

  return `<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#0F172A;font-family:'Segoe UI',Arial,sans-serif;color:#E2E8F0">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#0F172A;padding:24px 0">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background:#1E293B;border-radius:12px;overflow:hidden;border:1px solid #334155">

  <!-- Header -->
  <tr><td style="background:linear-gradient(135deg,#1E3A8A,#1E293B);padding:24px 32px">
    <table width="100%"><tr>
      <td><span style="font-size:22px;font-weight:700;color:#fff">📊 Numista.AI</span><br>
          <span style="font-size:13px;color:#94A3B8">Beta Feedback Alert</span></td>
      <td align="right">
        <span style="background:${sev.hex};color:#fff;padding:6px 16px;border-radius:20px;font-size:14px;font-weight:700">
          ${sev.emoji} ${sev.label}
        </span>
      </td>
    </tr></table>
  </td></tr>

  <!-- Core info row -->
  <tr><td style="padding:20px 32px 0">
    <table width="100%" style="border-collapse:collapse">
      <tr>
        <td style="padding:8px 12px;background:#0F172A;border-radius:8px;width:48%">
          <div style="font-size:11px;color:#64748B;text-transform:uppercase;letter-spacing:1px">Issue Type</div>
          <div style="font-size:15px;font-weight:600;color:#F1F5F9;margin-top:4px">${issueLabel}</div>
        </td>
        <td style="width:4%"></td>
        <td style="padding:8px 12px;background:#0F172A;border-radius:8px;width:48%">
          <div style="font-size:11px;color:#64748B;text-transform:uppercase;letter-spacing:1px">Intake Method</div>
          <div style="font-size:15px;font-weight:600;color:#F1F5F9;margin-top:4px">${method}</div>
        </td>
      </tr>
      <tr><td colspan="3" style="height:8px"></td></tr>
      <tr>
        <td style="padding:8px 12px;background:#0F172A;border-radius:8px">
          <div style="font-size:11px;color:#64748B;text-transform:uppercase;letter-spacing:1px">Page</div>
          <div style="font-size:14px;color:#F1F5F9;margin-top:4px">${doc.page_title || '/'} <span style="color:#64748B;font-size:12px">(${doc.route || '/'})</span></div>
        </td>
        <td style="width:4%"></td>
        <td style="padding:8px 12px;background:#0F172A;border-radius:8px">
          <div style="font-size:11px;color:#64748B;text-transform:uppercase;letter-spacing:1px">User</div>
          <div style="font-size:14px;color:#F1F5F9;margin-top:4px">${doc.user_email || doc.user_id || 'Unknown'}</div>
        </td>
      </tr>
    </table>
  </td></tr>

  <!-- MORGAN Summary -->
  <tr><td style="padding:20px 32px 0">
    <div style="font-size:12px;color:#64748B;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">MORGAN's Summary</div>
    <div style="background:#0F172A;border-left:3px solid #3B82F6;padding:12px 16px;border-radius:0 8px 8px 0;font-size:14px;color:#CBD5E1;line-height:1.6">
      ${doc.morgan_summary || doc.morgan_summary_confirmed_text || '<em style="color:#64748B">No summary available</em>'}
    </div>
  </td></tr>

  <!-- AI Guidance box -->
  <tr><td style="padding:20px 32px 0">
    <div style="background:#1A2744;border:1px solid #2D4A8A;border-radius:10px;padding:16px 20px">
      <div style="font-size:13px;font-weight:700;color:#60A5FA;margin-bottom:12px">🤖 AI Triage Guidance</div>
      <table width="100%" style="border-collapse:collapse">
        <tr><td style="padding:0 0 10px">
          <div style="font-size:11px;color:#6B7280;text-transform:uppercase;letter-spacing:0.8px">Root Cause Hypothesis</div>
          <div style="font-size:13px;color:#E2E8F0;margin-top:3px">${analysis.root_cause_hypothesis || '—'}</div>
        </td></tr>
        <tr><td style="padding:0 0 10px;border-top:1px solid #1E3A8A">
          <div style="font-size:11px;color:#6B7280;text-transform:uppercase;letter-spacing:0.8px;margin-top:10px">Suggested Fix Area</div>
          <div style="font-size:13px;color:#93C5FD;margin-top:3px;font-family:monospace">${analysis.suggested_fix_area || '—'}</div>
        </td></tr>
        <tr><td style="padding:0 0 10px;border-top:1px solid #1E3A8A">
          <div style="font-size:11px;color:#6B7280;text-transform:uppercase;letter-spacing:0.8px;margin-top:10px">Priority Rationale</div>
          <div style="font-size:13px;color:#E2E8F0;margin-top:3px">${analysis.priority_rationale || '—'}</div>
        </td></tr>
        <tr><td style="border-top:1px solid #1E3A8A;padding-top:10px">
          <span style="font-size:11px;color:#6B7280;text-transform:uppercase;letter-spacing:0.8px">Effort: </span>
          <span style="color:${effortHex};font-weight:700;font-size:13px">${(analysis.estimated_effort || 'unknown').toUpperCase()}</span>
          &nbsp;&nbsp;
          ${tagChips}
        </td></tr>
      </table>
    </div>
  </td></tr>

  <!-- Screenshot -->
  <tr><td style="padding:16px 32px 0">
    <div style="font-size:12px;color:#64748B;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">Screenshot</div>
    ${screenshotBlock}
  </td></tr>

  <!-- Transcript preview -->
  ${transcriptRows ? `
  <tr><td style="padding:16px 32px 0">
    <div style="font-size:12px;color:#64748B;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">Interview Transcript (preview)</div>
    <table width="100%" style="border-radius:8px;overflow:hidden;border:1px solid #1E293B">${transcriptRows}</table>
  </td></tr>` : ''}

  <!-- CTA -->
  <tr><td style="padding:24px 32px" align="center">
    <a href="https://numista.ai" style="background:#1D4ED8;color:#fff;padding:12px 32px;border-radius:8px;text-decoration:none;font-weight:600;font-size:14px;display:inline-block">
      Open Admin Feedback Screen →
    </a>
  </td></tr>

  <!-- Footer -->
  <tr><td style="padding:16px 32px 24px;border-top:1px solid #1E293B">
    <p style="font-size:11px;color:#64748B;margin:0">
      Feedback ID: <code style="color:#94A3B8">${doc.feedback_id || 'unknown'}</code> &nbsp;·&nbsp;
      App Version: ${doc.app_version || '—'} &nbsp;·&nbsp;
      Turns: ${doc.interview_turns || 0}
    </p>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>`;
}

module.exports = { buildEmailHtml };
