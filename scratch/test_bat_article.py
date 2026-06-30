import sys
sys.path.append("c:/Users/ericd/Documents/MyVertexProject/numista_backend")
from botasaurus.request import request, Request
from botasaurus.soupify import soupify

@request
def inspect_bat_article(request: Request, data=None):
    url = "https://coinweek.com/grab-the-tinfoil-people-on-the-internet-are-going-batshit-over-2020-samoa-atb-quarter/"
    resp = request.get(url)
    soup = soupify(resp)
    
    print("--- ARTICLE TEXT ---")
    paragraphs = [p.get_text() for p in soup.find_all("p")]
    print("\n".join(paragraphs[:8]))
    
    print("\n--- IMAGES ---")
    for img in soup.find_all("img", src=True):
        print(f"src: {img['src']}")
        print(f"alt: {img.get('alt')}")

if __name__ == "__main__":
    inspect_bat_article()
