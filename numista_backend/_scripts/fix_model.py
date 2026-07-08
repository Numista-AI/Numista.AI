with open("auto_annotate_checklist_dataset.py", "r", encoding="utf-8") as f:
    code = f.read()
code = code.replace('GEMINI_MODEL       = "gemini-3.5-flash-001"', r'''# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
GEMINI_MODEL       = "gemini-3.5-flash"''')
with open("auto_annotate_checklist_dataset.py", "w", encoding="utf-8") as f:
    f.write(code)
print("Model updated:", "gemini-3.5-flash" in code)
