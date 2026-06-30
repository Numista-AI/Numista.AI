import urllib.parse
from botasaurus.request import request, Request
from botasaurus.soupify import soupify

@request
def inspect_h2(request: Request, query):
    url = f"https://www.error-ref.com/?s={urllib.parse.quote_plus(query)}"
    resp = request.get(url)
    soup = soupify(resp)
    
    print("--- h2 tags ---")
    for h2 in soup.find_all("h2"):
        print(f"h2 text: {h2.get_text().strip()}")
        print(f"h2 class: {h2.get('class')}")
        a = h2.find("a", href=True)
        if a:
            print(f"  a: {a['href']}")

if __name__ == "__main__":
    inspect_h2("die gouge")
