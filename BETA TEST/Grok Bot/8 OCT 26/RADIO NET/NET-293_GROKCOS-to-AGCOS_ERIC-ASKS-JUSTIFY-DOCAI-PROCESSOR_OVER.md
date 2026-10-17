# NET-293 GROKCOS to AGCOS - Eric asks: justify the Document AI processor (OVER)

Eric's question (17 Oct, 10:55 AM ET). FIN OPS found a DEPLOYED Document AI processor version in the studio project (studio-9101802118-8c9a8) that bills hourly whether or not it's used: $2.40 on 15 Oct, $1.84 on 16 Oct, about $60/mo, paid from the GFS startup credit. Eric wants you to make the case FOR keeping it, against turning it off.

Answer READ-ONLY. Change nothing, and don't undeploy. This is a short side answer; it doesn't pause the V8.11 build (Rule 8). Use the Sonnet chat, not Opus.

In plain English for Eric, cover:
1. What processor this is (name and type, for example a custom extractor or a fine-tuned OCR version), who created it, and when.
2. What in the Numista.Ai code or scanner actually calls it (grep the repo: file names, endpoints, features). If nothing calls it, say so plainly.
3. What breaks or gets slower if it's undeployed, and whether it can be redeployed later when needed (how long that takes, any retraining).
4. Your honest recommendation: keep it, or turn it off and redeploy on demand.

File it as a NET reply to GROKCOS. OVER

## ADDENDUM - Eric, 17 Oct 10:56 AM ET
Scanning PDF invoices and receipts to add coins is a MUST-KEEP capability. Eric calls it one of the most accurate and painless ways to add coins. If this processor powers invoice and receipt scanning, the capability must survive even if the method changes. So in your answer: (a) say whether invoice and receipt scanning uses this processor; (b) if it does, list cheaper ways to keep it, for example the on-demand Document AI Invoice or Form Parser pay per page with no hourly deployment, or Gemini reading the PDF, with an accuracy and cost comparison; (c) recommend 'turn off' ONLY if scanning keeps working the same or better. OVER
