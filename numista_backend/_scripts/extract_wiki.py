import json
try:
    import fitz
    doc = fitz.open(r"C:\Users\ericd\Documents\MyVertexProject\Coin program Training Data\American Innovation Dollars\American Innovation Dollars.pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    
    with open("wiki_pdf_text.txt", "w", encoding='utf-8') as f:
        f.write(text)
    print("Extracted to wiki_pdf_text.txt - Length:", len(text))
except Exception as e:
    print("fitz failed, trying PyPDF2", e)
    import PyPDF2
    with open(r"C:\Users\ericd\Documents\MyVertexProject\Coin program Training Data\American Innovation Dollars\American Innovation Dollars.pdf", "rb") as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        with open("wiki_pdf_text.txt", "w", encoding='utf-8') as f:
            f.write(text)
        print("Extracted to wiki_pdf_text.txt via PyPDF2 - Length:", len(text))
