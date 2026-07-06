# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
with open("auto_annotate_checklist_dataset.py", "r", encoding="utf-8") as f:
    code = f.read()
old = 'GCP_PROJECT_ID     = "studio-dev-project"'
new = 'GCP_PROJECT_ID     = "studio-9101802118-8c9a8"'
code = code.replace(old, new)
with open("auto_annotate_checklist_dataset.py", "w", encoding="utf-8") as f:
    f.write(code)
print("Project ID updated:", new in code)
