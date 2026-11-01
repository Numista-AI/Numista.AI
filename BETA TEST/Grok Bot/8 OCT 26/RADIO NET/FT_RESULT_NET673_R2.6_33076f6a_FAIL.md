# FT RESULT NET-647 R2.6 (NET-673): OVERALL FAIL
p7-gate preview, tested as grokbot. 31 Oct 2026, about 7:48 PM ET. Nothing was committed, nothing was deleted, and live, main and dev were not touched.
| # | Check | Result | What I saw |
|---|---|---|---|
|1|Thumbnails|FAIL|The 7 single-coin cards show the gold "$" placeholder. The 2 set cards show a set image, not a coin side. I counted 9 cards, not 11.|
|2|Roll $2.44 each|PASS|$2.44 each, QTY 25, $61.00 total. The Invoice # field shows N/A.|
|3|2-coin sets $32.49/$84.50|FAIL|Morgan EU x2 shows $169.00 each. Innovation x2 shows $64.97 each.|
|4|Location persists|PASS|Saved with no error and was still there after a reload. The app dropped some typed characters.|
|5|Build stamp 33076f6a|PASS|/version.json shows git_commit 33076f6a. The UI banner shows v8.18.15h with no hash.|
|6|Upload Invoice|PASS|USM23493262 gave 1 coin at $134.45 with no error. Its new row also shows the "$" placeholder and was left uncommitted.|
Screenshots are in shots_net673.tar.gz.
