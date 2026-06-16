filepath = r'c:\Users\ericd\Documents\MyVertexProject\numista_mobile\lib\screens\my_collection_screen.dart'
with open(filepath, 'rb') as f:
    raw = f.read()

# Replace the one remaining em-dash (U+2014, UTF-8: e2 80 94) with ' - '
em_dash = b'\xe2\x80\x94'
fixed = raw.replace(em_dash, b' - ')
count = raw.count(em_dash)
print(f'Replaced {count} em-dash(es)')

with open(filepath, 'wb') as f:
    f.write(fixed)
print('Done.')
