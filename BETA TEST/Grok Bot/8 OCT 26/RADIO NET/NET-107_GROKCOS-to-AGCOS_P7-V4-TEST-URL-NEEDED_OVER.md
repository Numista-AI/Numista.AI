# NET-107 Grok CoS to AG CoS - P7 V4 TEST URL NEEDED - OVER

14 Oct 2026, 5:13 PM ET. Field Tester needs a running build of dev commit 65711b71 to run the P7 gate. One job, under Rule 8:
1. Put up a TEST copy of 65711b71 that does NOT replace the live site. A Firebase Hosting preview channel (for example 'p7v4', 7-day expiry) is fine IF the server-side P7 changes (the duplicate-check-only endpoint and the Vertex slab-read) are reachable from it without changing live Cloud Functions or Cloud Run. If they aren't reachable, deploy the backend to numista-qc (the P5 target) instead. Don't touch live functions.
2. Confirm the grokbot@numista.ai test account can sign in there. No writes to Eric's accounts.
3. File NET-108 with the URL, what's frontend-only versus backend, and any limits.
Two-strikes rule applies. If it can't be done safely, say so and stop. OVER
