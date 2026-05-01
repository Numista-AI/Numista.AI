"""
build_architecture_html.py
Converts ARCHITECTURE.md into a polished, printable HTML file.
Run: python build_architecture_html.py
Output: ARCHITECTURE.html  (open in any browser -> Ctrl+P -> Save as PDF)
"""
import markdown
import pathlib

MD_FILE   = pathlib.Path(__file__).parent / "ARCHITECTURE.md"
HTML_FILE = pathlib.Path(__file__).parent / "ARCHITECTURE.html"

md_text = MD_FILE.read_text(encoding="utf-8")

body_html = markdown.markdown(
    md_text,
    extensions=["tables", "fenced_code", "toc", "nl2br"],
)

CSS = """
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
  :root {
    --primary: #1565C0;
    --accent:  #F63366;
    --bg:      #F0F4F8;
    --surface: #FFFFFF;
    --border:  #E2E6E9;
    --text:    #1E293B;
    --sub:     #64748B;
    --code-bg: #0F172A;
    --code-fg: #E2E8F0;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Inter', system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    font-size: 14px;
    line-height: 1.75;
    padding: 48px 24px;
  }
  .wrapper { max-width: 960px; margin: 0 auto; }

  /* Cover card */
  .cover {
    background: linear-gradient(135deg, #1565C0 0%, #0D47A1 55%, #1A237E 100%);
    color: #fff;
    border-radius: 16px;
    padding: 56px 52px;
    margin-bottom: 48px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(21,101,192,0.35);
  }
  .cover::before {
    content: '';
    position: absolute; bottom: -80px; right: -80px;
    width: 320px; height: 320px;
    border-radius: 50%;
    background: rgba(255,255,255,0.06);
  }
  .cover .eyebrow { font-size: 11px; font-weight: 600; letter-spacing: 2px; opacity: 0.65; text-transform: uppercase; margin-bottom: 10px; }
  .cover h1 { font-size: 40px; font-weight: 700; letter-spacing: -0.5px; margin-bottom: 14px; }
  .cover .meta { font-size: 13px; opacity: 0.7; display: flex; gap: 24px; flex-wrap: wrap; }
  .cover .badge {
    display: inline-block; margin-top: 20px;
    background: rgba(246,51,102,0.85);
    border-radius: 20px; padding: 4px 14px;
    font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;
  }

  /* Content */
  h1 { font-size: 28px; font-weight: 700; color: var(--primary); margin: 52px 0 16px; padding-bottom: 10px; border-bottom: 2px solid var(--border); }
  h2 { font-size: 20px; font-weight: 600; color: var(--text); margin: 36px 0 12px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }
  h3 { font-size: 16px; font-weight: 600; color: var(--primary); margin: 28px 0 8px; }
  h4 { font-size: 12px; font-weight: 700; color: var(--sub); margin: 20px 0 6px; text-transform: uppercase; letter-spacing: 0.8px; }
  p  { margin-bottom: 12px; }
  a  { color: var(--primary); }
  ul, ol { padding-left: 22px; margin-bottom: 12px; }
  li { margin-bottom: 5px; }
  strong { font-weight: 600; }
  hr { border: none; border-top: 1px solid var(--border); margin: 32px 0; }

  blockquote {
    border-left: 4px solid var(--accent);
    background: #FFF5F7;
    border-radius: 0 8px 8px 0;
    padding: 12px 18px;
    margin: 16px 0;
    color: #9D174D;
    font-size: 13px;
    font-weight: 500;
  }
  blockquote p { margin: 0; }

  code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    background: #EEF2FF;
    color: #DC2626;
    padding: 2px 6px;
    border-radius: 4px;
  }
  pre {
    background: var(--code-bg);
    color: var(--code-fg);
    border-radius: 10px;
    padding: 20px 24px;
    overflow-x: auto;
    margin: 14px 0 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    line-height: 1.65;
    box-shadow: 0 4px 16px rgba(0,0,0,0.18);
  }
  pre code { background: none; color: inherit; padding: 0; font-size: 12px; }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0 22px;
    background: var(--surface);
    border-radius: 10px;
    overflow: hidden;
    font-size: 13px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.07);
  }
  th {
    background: var(--primary);
    color: #fff;
    font-weight: 600;
    padding: 11px 16px;
    text-align: left;
    font-size: 12px;
    letter-spacing: 0.2px;
  }
  td { padding: 10px 16px; border-bottom: 1px solid var(--border); vertical-align: top; }
  tr:last-child td { border-bottom: none; }
  tr:nth-child(even) td { background: #F8FAFC; }

  /* TOC */
  .toc {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px 24px;
    margin: 0 0 44px;
  }
  .toc > h4 { margin-top: 0; }
  .toc ul { list-style: none; padding: 0; }
  .toc li { padding: 4px 0; border-bottom: 1px dotted var(--border); }
  .toc li:last-child { border-bottom: none; }
  .toc a { color: var(--primary); font-size: 13px; }

  @media print {
    body { background: #fff; padding: 16px; font-size: 12px; }
    .cover { border-radius: 8px; page-break-inside: avoid; }
    pre { white-space: pre-wrap; word-break: break-all; box-shadow: none; }
    h1, h2 { page-break-after: avoid; }
    table { box-shadow: none; }
  }
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Numista.AI — System Architecture</title>
  <style>{css}</style>
</head>
<body>
<div class="wrapper">

  <div class="cover">
    <div class="eyebrow">Numista.AI</div>
    <h1>System Architecture</h1>
    <div class="meta">
      <span>&#128197; Version: May 2026</span>
      <span>&#128100; Author: Numista Deployer</span>
      <span>&#9729; GCP: studio-9101802118-8c9a8</span>
    </div>
    <div class="badge">Beta MVP</div>
  </div>

  {body}

</div>
</body>
</html>
"""

html_out = HTML_TEMPLATE.format(css=CSS, body=body_html)
HTML_FILE.write_text(html_out, encoding="utf-8")
print(f"Done! Saved to: {HTML_FILE}")
print()
print("To save as PDF:")
print("  1. Double-click ARCHITECTURE.html to open in your browser")
print("  2. Press Ctrl+P")
print("  3. Set Destination to 'Save as PDF'")
print("  4. Click Save")
