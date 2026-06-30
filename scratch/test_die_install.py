import sys
sys.path.append("c:/Users/ericd/Documents/MyVertexProject/numista_backend")
from botasaurus.request import request, Request
from botasaurus.soupify import soupify

@request
def inspect_die_install(request: Request, data=None):
    url = "https://www.error-ref.com/inverted-dioe-installation/"
    resp = request.get(url)
    soup = soupify(resp)
    
    print("--- PAGE TEXT ---")
    print(soup.get_text()[:1000])
    
    print("\n--- IMAGES ---")
    for img in soup.find_all("img", src=True):
        print(f"src: {img['src']}")
        print(f"alt: {img.get('alt')}")

if __name__ == "__main__":
    inspect_die_install()
