import zipfile
import xml.etree.ElementTree as ET

def read_docx(file_path):
    try:
        with zipfile.ZipFile(file_path) as docx:
            xml_content = docx.read('word/document.xml')
            root = ET.fromstring(xml_content)
            
            # Find all paragraph elements
            paragraphs = []
            for para in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                text_elems = para.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')
                text = ''.join([elem.text for elem in text_elems if elem.text])
                if text:
                    paragraphs.append(text)
            
            return '\n'.join(paragraphs)
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    import os
    path = r"c:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\Sheldon 1-70 scale.docx"
    print(read_docx(path))
