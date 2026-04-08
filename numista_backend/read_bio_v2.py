import zipfile
import xml.etree.ElementTree as ET
import sys
import re

def get_docx_text_better(path):
    try:
        with zipfile.ZipFile(path) as document:
            xml_content = document.read('word/document.xml')
            
        # Register namespaces to make finding easier
        namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        }
        
        tree = ET.fromstring(xml_content)
        
        full_text = []
        for p in tree.findall('.//w:p', namespaces):
            texts = [node.text for node in p.findall('.//w:t', namespaces) if node.text]
            if texts:
                full_text.append(''.join(texts))
            else:
                # Add empty line for empty paragraphs to preserve spacing
                full_text.append('')
                
        return '\n'.join(full_text)
    except Exception as e:
        return f"Error: {e}"

print(get_docx_text_better("My Bio Numista.AI.docx"))
