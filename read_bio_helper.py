import docx

def getText(filename):
    doc = docx.Document(filename)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return '\n\n'.join(fullText)

try:
    print(getText("My Bio Numista.AI.docx"))
except Exception as e:
    print(f"Error: {e}")
