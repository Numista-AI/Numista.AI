# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
filepath = r'c:\Users\ericd\Documents\MyVertexProject\numista_mobile\lib\screens\my_collection_screen.dart'
with open(filepath, 'rb') as f:
    raw = f.read()

em_dash_utf8 = b'\xe2\x80\x94'
arrow_utf8 = b'\xe2\x86\x92'
book_emoji = b'\xf0\x9f\x93\x96'

print(f'File size: {len(raw)} bytes')
print(f'Em-dash occurrences: {raw.count(em_dash_utf8)}')
print(f'Right-arrow occurrences: {raw.count(arrow_utf8)}')
print(f'Book emoji occurrences: {raw.count(book_emoji)}')
print(f'BOM present: {raw[:3] == b"\\xef\\xbb\\xbf"}')

# Try to decode as UTF-8 to verify the file is valid UTF-8
try:
    text = raw.decode('utf-8')
    print('File decodes as valid UTF-8')
except UnicodeDecodeError as e:
    print(f'UTF-8 decode error: {e}')

# Find context around em-dashes
import re
text = raw.decode('utf-8', errors='replace')
for i, line in enumerate(text.split('\n'), 1):
    if '\u2014' in line or '\u2192' in line or '\U0001f4d6' in line:
        print(f'  Line {i}: {line.strip()[:100]}')
