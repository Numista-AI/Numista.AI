"""Fix: add response_mime_type=application/json to gemini_extract_from_text."""
with open("auto_annotate_checklist_dataset.py", "r", encoding="utf-8") as f:
    code = f.read()

old = (
    "        response = gemini_model.generate_content(\n"
    "            [Part.from_text(prompt)],\n"
    "            generation_config=GenerationConfig(\n"
    "                response_mime_type=\"application/json\", temperature=0.0, max_output_tokens=8192),\n"
    "        )"
)
# Check if it's already there
if old in code:
    print("Already fixed — no change needed.")
else:
    # The text-only call inside gemini_extract_from_text currently lacks response_mime_type
    # Find the function and fix it
    old2 = (
        "        response = gemini_model.generate_content(\n"
        "            [Part.from_text(prompt)],\n"
        "            generation_config=GenerationConfig(\n"
        "                temperature=0.0, max_output_tokens=8192),\n"
        "        )"
    )
    new2 = (
        "        response = gemini_model.generate_content(\n"
        "            [Part.from_text(prompt)],\n"
        "            generation_config=GenerationConfig(\n"
        "                response_mime_type=\"application/json\", temperature=0.0, max_output_tokens=8192),\n"
        "        )"
    )
    if old2 in code:
        code = code.replace(old2, new2)
        print("Fixed: added response_mime_type to text-based extraction.")
    else:
        print("Pattern not found — searching for the function block...")
        # Show lines around gemini_extract_from_text
        for i, line in enumerate(code.splitlines()):
            if "gemini_extract_from_text" in line or "Part.from_text(prompt)" in line:
                print(f"  Line {i}: {repr(line)}")

with open("auto_annotate_checklist_dataset.py", "w", encoding="utf-8") as f:
    f.write(code)
print("Done.")
