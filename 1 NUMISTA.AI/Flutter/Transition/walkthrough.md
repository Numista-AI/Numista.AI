# IDE Configuration and Authentication Fix Walkthrough

I have performed the "definitive actions" requested to force the bridge to Vertex AI and clear any stale configurations.

### Changes Made

1. **Global `settings.json` Override**:
   - **File**: `C:\Users\ericd\AppData\Roaming\Antigravity\User\settings.json`
   - **Action**: Forced the following entries to point the IDE at Vertex AI using project `studio-9101802118-8c9a8`.
     - `"google.gemini.provider": "vertex-ai"`
     - `"google.gemini.vertexAi.projectId": "studio-9101802118-8c9a8"`
     - Updated `"geminicodeassist.project"` as well.

2. **Authentication Cache Purge**:
   - **Command Run**: Attempted to delete `Local Storage`, `Cache`, `Code Cache`, and `Session Storage` in `%APPDATA%\Antigravity`.
   - **Note**: Some files may have been locked by the current running session. The purge will be fully effective only after you restart the IDE.

---

### CRITICAL: Final Steps for the User

> [!IMPORTANT]
> **RESTART THE IDE NOW.** 
> Close every instance of the IDE and then relaunch it.
> 1. You will be prompted to log in again. Use your `eric@numista.ai` account.
> 2. Once logged in, go to the model selector (bottom right or in the chat window).
> 3. Verify that the "Provider" shows **Vertex AI** and the project is **`studio-9101802118-8c9a8`**.

This should bypass the $450/month "Enterprise" subscription wall by routing directly through your Vertex AI billing.
