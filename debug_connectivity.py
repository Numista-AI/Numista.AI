
import vertexai
from vertexai.generative_models import GenerativeModel
import google.cloud.aiplatform as aip

PROJECT_ID = "studio-9101802118-8c9a8"

def list_models_in_location(location):
    print(f"\n--- Listing Models in {location} ---")
    try:
        aip.init(project=PROJECT_ID, location=location)
        models = aip.Model.list() # This lists custom models
        print(f"Custom Models found: {len(models)}")
        for m in models: print(f"- {m.display_name}")
        
        # List Publisher Models (Gemini foundation models)
        # There isn't a direct simple SDK method to listing *all* foundation models easily without pagination 
        # but we can try to just init one that we know *should* work if permissions are right.
        
        print("Checking Foundation Model reachability...")
        # Just attempting to get the model resource usage the Model Garden API logic often hidden
        # Instead, we will try to just print the error of a known 'safe' one to see if it's different.
        
    except Exception as e:
        print(f"Error listing models: {e}")

# We'll use a specific script to list PREDICITON models via the lower level API if needed, 
# but for now let's just use the `gcloud` equivalent if possible? 
# No, sticking to python.
# Actually, `vertexai.preview.language_models` aren't what we want.
# Let's try to just list capability.

from google.cloud import aiplatform
def list_foundation_models(location):
    print(f"--- Foundation Models in {location} ---")
    aiplatform.init(project=PROJECT_ID, location=location)
    # This is often the permission choke point
    try:
        # Generic check
        print("AI Platform initialized.")
    except Exception as e:
        print(f"Init failed: {e}")

list_foundation_models("us-central1")
list_foundation_models("us-east4")
