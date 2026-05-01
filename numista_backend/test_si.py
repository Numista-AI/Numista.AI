import re

html_path = r"C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images\si_quarters\American Women Quarters™ Program _ Smithsonian American Women's History Museum.html"

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Find image tags
matches = re.findall(r'<img[^>]+src=[\"\']([^\"\']+)[\"\']', html)
print(f"Found {len(matches)} image tags.")

image_urls = []
for m in matches:
    if 'quarter' in m.lower() or 'awq' in m.lower() or 'usmint' in m.lower() or 'coin' in m.lower():
        image_urls.append(m)

print("\nRelevant Images:")
for img in set(image_urls):
    print(img)
