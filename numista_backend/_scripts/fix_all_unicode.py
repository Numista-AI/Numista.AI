# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
Comprehensive fix: Replace ALL em-dashes, en-dashes, and other problematic Unicode
in the Dart source file with ASCII-safe alternatives.
This covers characters in both string literals and comments.
"""
filepath = r'c:\Users\ericd\Documents\MyVertexProject\numista_mobile\lib\screens\my_collection_screen.dart'

with open(filepath, 'rb') as f:
    raw = f.read()

replacements = [
    (b'\xe2\x80\x94', b' - '),   # U+2014 em dash —
    (b'\xe2\x80\x93', b' - '),   # U+2013 en dash –
    (b'\xe2\x80\x92', b' - '),   # U+2012 figure dash
    (b'\xe2\x80\x95', b' - '),   # U+2015 horizontal bar
    (b'\xe2\x86\x92', b'>'),     # U+2192 right arrow →
    (b'\xf0\x9f\x93\x96', b''), # U+1F4D6 book emoji 📖
]

total_fixed = 0
result = raw
for pattern, repl in replacements:
    count = result.count(pattern)
    if count > 0:
        print(f'  Replacing {count}x {pattern.hex()} -> {repl}')
        result = result.replace(pattern, repl)
        total_fixed += count

with open(filepath, 'wb') as f:
    f.write(result)

print(f'\nTotal fixed: {total_fixed} occurrences')
print(f'File size: {len(raw)} -> {len(result)} bytes')

# Verify no more problem bytes
remaining_em = result.count(b'\xe2\x80\x94')
remaining_en = result.count(b'\xe2\x80\x93')
print(f'Remaining em-dashes: {remaining_em}')
print(f'Remaining en-dashes: {remaining_en}')
