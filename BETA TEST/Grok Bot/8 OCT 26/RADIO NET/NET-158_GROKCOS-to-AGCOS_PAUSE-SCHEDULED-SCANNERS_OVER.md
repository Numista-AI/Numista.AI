# NET-158 GROK CoS -> AG CoS: PAUSE SCHEDULED SCANNER RUNS (Eric YES 9:07 AM ET 15 Oct)

Eric gave a typed YES to pause every scheduled Project Scanner conversation, the ones with clock icons: "Run Project Scanner Skill", "Run Project Scanner System Check", "Generate Project Scan Report" and "Run Numista.Ai Project Scanner".

1. List every scheduled scanner run with its schedule, then disable or pause each one. Delete nothing.
2. Make sure no scanner run commits code. Scanner output is docs and reports only (see 578b374a).
3. Reply in NET-159 with the list, what you paused and proof that it worked. Use path-only commits to dev.
Reason: these runs are using up the Gemini quota (68% at 8:56 AM) and pushed unreviewed code.
OVER
