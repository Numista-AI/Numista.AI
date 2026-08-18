# Where files are being saved — working directory report

**Date:** 2026-08-17  
**Question:** Where are you currently saving files? Run `pwd`, `dir *.md`, `dir grok_build_output.md`. Full absolute path of the current working directory.

---

## Direct answer

Files from this Grok Build session are being saved in the **workspace / project root**:

**`C:\Users\ericd\Documents\MyVertexProject`**

That is the current working directory. The standing output file is:

**`C:\Users\ericd\Documents\MyVertexProject\grok_build_output.md`**

Earlier in this session, one copy of a GCS report was written under `Grok Advice\Grok Advisor\`. After the standing rule was set, all subsequent non-trivial answers have been overwritten at the project-root `grok_build_output.md` above.

---

## Command results

### `pwd`

PowerShell does not print a Unix-style `pwd` banner the same way bash does. Equivalent result from `(Get-Location).Path`:

```
C:\Users\ericd\Documents\MyVertexProject
```

`Get-Location` details:

```
Drive        : C
Provider     : Microsoft.PowerShell.Core\FileSystem
ProviderPath : C:\Users\ericd\Documents\MyVertexProject
Path         : C:\Users\ericd\Documents\MyVertexProject
```

### Full absolute path of the current working directory

```
C:\Users\ericd\Documents\MyVertexProject
```

### `dir *.md`

These are the `*.md` files in the current working directory only (project root, not recursive):

| Name | FullName | Length | LastWriteTime |
|---|---|---:|---|
| agent_guidance.md | C:\Users\ericd\Documents\MyVertexProject\agent_guidance.md | 8892 | 8/15/2026 11:56:46 AM |
| ARCHITECTURE.md | C:\Users\ericd\Documents\MyVertexProject\ARCHITECTURE.md | 25298 | 8/8/2026 7:28:50 PM |
| beta_feedback_rubric.md | C:\Users\ericd\Documents\MyVertexProject\beta_feedback_rubric.md | 2141 | 8/8/2026 7:28:50 PM |
| beta_test_script.md | C:\Users\ericd\Documents\MyVertexProject\beta_test_script.md | 3930 | 8/8/2026 7:28:50 PM |
| cdn_permission_request_letter.md | C:\Users\ericd\Documents\MyVertexProject\cdn_permission_request_letter.md | 2805 | 8/8/2026 7:28:50 PM |
| DEPLOYMENT_SOP.md | C:\Users\ericd\Documents\MyVertexProject\DEPLOYMENT_SOP.md | 8157 | 6/27/2026 12:21:10 PM |
| DEVELOPER_ONBOARDING.md | C:\Users\ericd\Documents\MyVertexProject\DEVELOPER_ONBOARDING.md | 3039 | 8/8/2026 7:28:50 PM |
| estate_logic_rules.md | C:\Users\ericd\Documents\MyVertexProject\estate_logic_rules.md | 3187 | 8/8/2026 7:28:50 PM |
| GRAY_SCREEN_INVESTIGATION_REPORT.md | C:\Users\ericd\Documents\MyVertexProject\GRAY_SCREEN_INVESTIGATION_REPORT.md | 10293 | 8/11/2026 2:19:41 PM |
| grok_build_output.md | C:\Users\ericd\Documents\MyVertexProject\grok_build_output.md | 11467* | 8/17/2026 10:06:18 AM* |
| grok_verification_sample.md | C:\Users\ericd\Documents\MyVertexProject\grok_verification_sample.md | 30119 | 6/26/2026 12:10:20 PM |
| implementation_plan 8 jun 26.md | C:\Users\ericd\Documents\MyVertexProject\implementation_plan 8 jun 26.md | 14110 | 6/8/2026 10:56:35 AM |
| Numista_AI_Architecture_Overview_AUG_2026.md | C:\Users\ericd\Documents\MyVertexProject\Numista_AI_Architecture_Overview_AUG_2026.md | 10985 | 8/7/2026 11:45:41 AM |
| Numista_AI_Architecture_Overview_JUN_2026.md | C:\Users\ericd\Documents\MyVertexProject\Numista_AI_Architecture_Overview_JUN_2026.md | 20076 | 6/25/2026 12:37:51 PM |
| NUMISTA_AI_CHECKLIST_DESIGN_SPEC.md | C:\Users\ericd\Documents\MyVertexProject\NUMISTA_AI_CHECKLIST_DESIGN_SPEC.md | 7557 | 4/16/2026 2:38:09 PM |
| Numista_AI_Developer_Blueprint_AUG_2026.md | C:\Users\ericd\Documents\MyVertexProject\Numista_AI_Developer_Blueprint_AUG_2026.md | 7941 | 8/7/2026 12:26:42 PM |
| Numista_AI_Developer_Blueprint_JUN_2026.md | C:\Users\ericd\Documents\MyVertexProject\Numista_AI_Developer_Blueprint_JUN_2026.md | 9726 | 6/25/2026 12:43:18 PM |
| Numista_AI_Ingestion_and_Data_Operations_Playbook_JUN_2026.md | C:\Users\ericd\Documents\MyVertexProject\Numista_AI_Ingestion_and_Data_Operations_Playbook_JUN_2026.md | 6687 | 6/25/2026 12:43:32 PM |
| NUMISTA_AI_SESSION_REPORT_APRIL_10.md | C:\Users\ericd\Documents\MyVertexProject\NUMISTA_AI_SESSION_REPORT_APRIL_10.md | 3041 | 4/10/2026 5:03:00 PM |
| NUMISTA_AI_SESSION_REPORT_APRIL_11.md | C:\Users\ericd\Documents\MyVertexProject\NUMISTA_AI_SESSION_REPORT_APRIL_11.md | 9414 | 4/11/2026 3:25:16 PM |
| NUMISTA_AI_SESSION_REPORT_APRIL_16.md | C:\Users\ericd\Documents\MyVertexProject\NUMISTA_AI_SESSION_REPORT_APRIL_16.md | 2758 | 4/16/2026 3:51:56 PM |
| Numista_Database_Audit_Manifest.md | C:\Users\ericd\Documents\MyVertexProject\Numista_Database_Audit_Manifest.md | 4807 | 6/26/2026 2:23:33 PM |
| PROD_BUILD_CHECKLIST.md | C:\Users\ericd\Documents\MyVertexProject\PROD_BUILD_CHECKLIST.md | 3423 | 6/22/2026 6:43:50 PM |
| README.md | C:\Users\ericd\Documents\MyVertexProject\README.md | 3771 | 8/8/2026 7:28:50 PM |
| RELEASE_NOTES.md | C:\Users\ericd\Documents\MyVertexProject\RELEASE_NOTES.md | 78759 | 8/17/2026 7:32:44 AM |
| REPOSITORY_RULES.md | C:\Users\ericd\Documents\MyVertexProject\REPOSITORY_RULES.md | 8803 | 8/13/2026 11:09:31 AM |
| SCAN_REPORT.md | C:\Users\ericd\Documents\MyVertexProject\SCAN_REPORT.md | 5986 | 8/17/2026 10:09:51 AM |
| SCHEDULED_JOBS.md | C:\Users\ericd\Documents\MyVertexProject\SCHEDULED_JOBS.md | 3817 | 8/8/2026 7:28:50 PM |
| SESSION_LOG.md | C:\Users\ericd\Documents\MyVertexProject\SESSION_LOG.md | 10415 | 8/12/2026 7:48:11 PM |
| SESSION_SUMMARY.md | C:\Users\ericd\Documents\MyVertexProject\SESSION_SUMMARY.md | 2040 | 4/9/2026 4:04:45 PM |
| SOURCE_OF_TRUTH.md | C:\Users\ericd\Documents\MyVertexProject\SOURCE_OF_TRUTH.md | 4885 | 6/23/2026 7:34:54 PM |
| walkthrough.md | C:\Users\ericd\Documents\MyVertexProject\walkthrough.md | 2194 | 8/15/2026 9:40:35 AM |

\* Size and timestamp of `grok_build_output.md` above are from the `dir` run **before** this overwrite. After this write, those values change.

**Count:** 32 markdown files in the project root.

### `dir grok_build_output.md`

```
Name          : grok_build_output.md
FullName      : C:\Users\ericd\Documents\MyVertexProject\grok_build_output.md
Length        : 11467
LastWriteTime : 8/17/2026 10:06:18 AM
DirectoryName : C:\Users\ericd\Documents\MyVertexProject
```

The file exists at the project root. The previous content (sourcing findings for Fr. 91 PCBLIC, T-43 reverse, and 2026 circulating coins) was last written at **8/17/2026 10:06:18 AM** and is overwritten by this report per the standing rule.

---

## Where session files have been saved (this conversation)

| File / artifact | Absolute path | Notes |
|---|---|---|
| Standing response file (current) | `C:\Users\ericd\Documents\MyVertexProject\grok_build_output.md` | Overwritten each non-trivial turn |
| Earlier GCS report copy | `C:\Users\ericd\Documents\MyVertexProject\Grok Advice\Grok Advisor\grok_build_output.md` | Written once before the standing root rule |
| Tracker work (prior turn) | `Gemini Advisor Documents\Grok Advisor\STATUS_TRACKER.md` and `Grok Advice\Grok Advisor\STATUS_TRACKER.md` | Documentation work, not the standing output file |

Shell commands run from:

```
C:\Users\ericd\Documents\MyVertexProject
```

That is the Grok Build workspace path (`Workspace Path: C:\Users\ericd\Documents\MyVertexProject`).
