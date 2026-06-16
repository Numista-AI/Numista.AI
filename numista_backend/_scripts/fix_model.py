with open("auto_annotate_checklist_dataset.py", "r", encoding="utf-8") as f:
    code = f.read()
code = code.replace('GEMINI_MODEL       = "gemini-2.0-flash-001"', 'GEMINI_MODEL       = "gemini-2.5-flash"')
with open("auto_annotate_checklist_dataset.py", "w", encoding="utf-8") as f:
    f.write(code)
print("Model updated:", "gemini-2.5-flash" in code)
