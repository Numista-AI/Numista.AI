import zipfile
import xml.etree.ElementTree as ET
import sys

def get_docx_text(path):
    document = zipfile.ZipFile(path)
    xml_content = document.read('word/document.xml')
    tree = ET.fromstring(xml_content)
    
    text = []
    for paragraph in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        texts = [node.text for node in paragraph.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text]
        if texts:
            text.append(''.join(texts))
    return '\n'.join(text)

try:
    print(get_docx_text("My Bio Numista.AI.docx"))
except Exception as e:
    print(f"Error reading docx: {e}")
