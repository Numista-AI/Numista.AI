"""
Fix DOUBLE-ENCODED UTF-8 in my_collection_screen.dart.

The file went through: original UTF-8 chars -> interpreted as cp1252 -> re-encoded as UTF-8.
To reverse: decode UTF-8 -> encode as cp1252 (undoing the second encoding) -> decode UTF-8 (get original).
Then replace the Unicode special chars with ASCII equivalents.
"""

TARGET = r"c:\Users\ericd\Documents\MyVertexProject\numista_mobile\lib\screens\my_collection_screen.dart"

with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Original length: {len(content)} chars")

# Try to reverse the double-encoding on each line
lines = content.split('\n')
fixed_lines = []
fix_count = 0

for i, line in enumerate(lines):
    # Check if line has non-ASCII characters that look like double-encoding
    has_suspect = any(ord(c) > 127 for c in line)
    if has_suspect:
        try:
            # Reverse the double-encoding:
            # 1. Encode back to bytes using cp1252 (the intermediate encoding)
            # 2. Decode those bytes as UTF-8 (getting original chars)
            restored = line.encode('cp1252').decode('utf-8')
            # Now replace Unicode special chars with ASCII
            restored = restored.replace('\u2014', '--')    # em-dash
            restored = restored.replace('\u2013', '-')     # en-dash
            restored = restored.replace('\u2026', '...')   # ellipsis
            restored = restored.replace('\u2022', '*')     # bullet
            restored = restored.replace('\u2500', '-')     # box-drawing
            restored = restored.replace('\U0001F50D', '')  # magnifying glass
            restored = restored.replace('\U0001F680', '')  # rocket
            restored = restored.replace('\u2019', "'")     # right single quote
            restored = restored.replace('\u201C', '"')     # left double quote
            restored = restored.replace('\u201D', '"')     # right double quote
            fixed_lines.append(restored)
            fix_count += 1
            if fix_count <= 10:
                print(f"  Line {i+1}: FIXED")
        except (UnicodeDecodeError, UnicodeEncodeError):
            # If the reverse-encoding fails, the line wasn't double-encoded
            # Just replace any remaining special chars directly
            cleaned = line
            cleaned = cleaned.replace('\u2026', '...')
            fixed_lines.append(cleaned)
            if has_suspect:
                print(f"  Line {i+1}: partial fix (could not fully reverse encoding)")
    else:
        fixed_lines.append(line)

result = '\n'.join(fixed_lines)

print(f"\nFixed {fix_count} lines")

# Verify no non-ASCII remains (except maybe in string literals that are intentional)
remaining = sum(1 for c in result if ord(c) > 127)
print(f"Remaining non-ASCII chars: {remaining}")

with open(TARGET, 'w', encoding='utf-8', newline='') as f:
    f.write(result)
print(f"File saved. New length: {len(result)} chars")
