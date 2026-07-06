# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""Patches auto_annotate_checklist_dataset.py to use text-based Gemini extraction."""

with open("auto_annotate_checklist_dataset.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Add the text-based Gemini function after the PDF-based one
text_gemini_fn = '''

def gemini_extract_from_text(gemini_model, doc_text):
    """
    Sends the OCR-extracted text to Gemini for entity extraction.
    Used when raw PDF bytes are not available in the Document AI dataset
    (training docs stored without content bytes).
    Returns {series_name, entries} dict or None.
    """
    # Build a compact structured prompt using the extracted text
    prompt = (
        EXTRACTION_PROMPT
        + "\\n\\n=== DOCUMENT TEXT (OCR extracted) ===\\n"
        + doc_text[:12000]  # Limit to avoid token overflow
    )
    try:
        response = gemini_model.generate_content(
            [Part.from_text(prompt)],
            generation_config=GenerationConfig(
                response_mime_type="application/json", temperature=0.0, max_output_tokens=8192),
        )
        return json.loads(response.text)
    except json.JSONDecodeError as e:
        print(f"    [Gemini] JSON parse error: {e}")
        return None
    except Exception as e:
        print(f"    [Gemini] Error: {e}")
        return None

'''

# Insert after the gemini_extract function
insert_after = "        return None\n\n\ndef build_document_entities"
code = code.replace(
    insert_after,
    "        return None\n" + text_gemini_fn + "\ndef build_document_entities"
)

# 2. Replace the PDF bytes fetch + gemini_extract call with text-only call
old_block = '''            pdf_bytes = doc_service.get_document(
                request=make_doc_id_request(doc_id, "content")).document.content
            if not pdf_bytes:
                print("    [Skip] No PDF bytes.")
                progress["skipped"].append(doc_id); save_progress(progress)
                time.sleep(SLEEP_BETWEEN_DOCS); continue
            print(f"    PDF:  {len(pdf_bytes)} bytes")

            print("    [Gemini] Extracting...")
            gemini_result = gemini_extract(gemini_model, pdf_bytes)'''

new_block = '''            # Training docs have no raw PDF bytes stored in the dataset.
            # Use OCR text (already fetched) directly with Gemini.
            print("    [Gemini] Extracting from OCR text...")
            gemini_result = gemini_extract_from_text(gemini_model, doc_text)'''

if old_block in code:
    code = code.replace(old_block, new_block)
    print("Block replaced successfully.")
else:
    print("ERROR: old_block not found in code. Check indentation.")

with open("auto_annotate_checklist_dataset.py", "w", encoding="utf-8") as f:
    f.write(code)

# Verify
assert "gemini_extract_from_text" in code, "Function not added"
assert "No PDF bytes" not in code, "Old PDF block still present"
print(f"Done. File size: {len(code)} chars")
