#!/usr/bin/env bash
set -e

WEB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../numista_mobile/web" && pwd)"
FAILED=0
TOTAL=0

echo "=========================================="
echo "Running node --check on HTML script blocks"
echo "=========================================="

for html_file in "$WEB_DIR"/*.html; do
  [ -f "$html_file" ] || continue
  TOTAL=$((TOTAL + 1))
  fname="$(basename "$html_file")"
  
  # Use node to extract and check inline scripts
  node - "$html_file" "$fname" << 'EOF'
const fs = require('fs');
const { execFileSync } = require('child_process');
const os = require('os');
const path = require('path');

const filePath = process.argv[2];
const fileName = process.argv[3];
const content = fs.readFileSync(filePath, 'utf8');

const scriptRegex = /<script(?:\s+[^>]*)?>([\s\S]*?)<\/script>/gi;
let match;
let idx = 0;
let fileFailed = false;

while ((match = scriptRegex.exec(content)) !== null) {
  idx++;
  const fullTag = match[0];
  const openingTag = fullTag.substring(0, fullTag.indexOf('>') + 1);
  if (/src\s*=/i.test(openingTag)) {
    continue; // external script
  }
  if (/type\s*=\s*['"]application\/ld\+json['"]/i.test(openingTag)) {
    try {
      JSON.parse(match[1]);
    } catch (e) {
      fileFailed = true;
      console.error(`FAIL: ${fileName} (JSON-LD block #${idx})`);
      console.error(e.message);
    }
    continue;
  }
  const isModule = /type\s*=\s*['"]module['"]/i.test(openingTag);
  const ext = isModule ? '.mjs' : '.js';
  const scriptContent = match[1];

  const tmpPath = path.join(os.tmpdir(), `check_${Date.now()}_${idx}${ext}`);
  fs.writeFileSync(tmpPath, scriptContent);

  try {
    execFileSync('node', ['--check', tmpPath], { stdio: 'pipe' });
  } catch (err) {
    fileFailed = true;
    console.error(`FAIL: ${fileName} (script block #${idx})`);
    if (err.stderr) console.error(err.stderr.toString());
  } finally {
    try { fs.unlinkSync(tmpPath); } catch (e) {}
  }
}

if (fileFailed) {
  process.exit(1);
} else {
  console.log(`PASS: ${fileName}`);
}
EOF

  if [ $? -ne 0 ]; then
    FAILED=$((FAILED + 1))
  fi
done

echo "=========================================="
echo "Summary: $((TOTAL - FAILED))/$TOTAL HTML files passed."

if [ $FAILED -gt 0 ]; then
  echo "ERROR: $FAILED HTML file(s) failed script check."
  exit 1
else
  echo "SUCCESS: All HTML scripts passed node --check."
  exit 0
fi
