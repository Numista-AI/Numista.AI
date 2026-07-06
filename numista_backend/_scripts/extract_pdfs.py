# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import sys

def extract_text(pdf_path, txt_path):
    text = ""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        print(f"Extracted {pdf_path} using PyMuPDF")
    except ImportError:
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            print(f"Extracted {pdf_path} using PyPDF2")
        except ImportError:
            try:
                import pdfplumber
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
                print(f"Extracted {pdf_path} using pdfplumber")
            except ImportError as e:
                print(f"No PDF library found. Please install PyMuPDF or PyPDF2. {e}")
                sys.exit(1)
                
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(text)

extract_text('LC-154-Eisenhower-Dollar-Checklist.pdf', 'eisenhower.txt')
extract_text('LC-8435-Presidential-Dollar-Checklist.pdf', 'presidential.txt')
