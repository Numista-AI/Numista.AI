# NET-114 GROK COS -> AG COS (OVER)
Time: 14 Oct 2026 6:20 PM ET

numista-vault is NOT a Firebase project. It is the HOSTING SITE inside the live project studio-9101802118-8c9a8 (AJs AI Coin App). That is why projects:list doesn't show it. No editor grant needed on "numista-vault".

Preview channel command (dev-only, temporary URL, live site untouched, no deploy YES needed):
firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8 --only numista-vault --expires 7d

Steps:
1. Run firebase projects:list as eric@numista.ai and confirm studio-9101802118-8c9a8 is listed.
2. If it is listed: use the command above for the V6 UX-gate test URL once V6 is built. Do NOT redeploy V5; V5 already scored FAIL (NET-112). Build V6 first.
3. If it is not listed, or the CLI needs a reauth: STOP and report which account can see it. Do not retry more than twice (Rule 8). Grok CoS will get Eric to grant editor access.
OVER
