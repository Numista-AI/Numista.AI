import urllib.parse
from botasaurus.request import request, Request
from botasaurus.soupify import soupify

@request
def inspect_h2(request: Request, query):
    url = f"https://www.error-ref.com/?s={urllib.parse.quote_plus(query)}"
    resp = request.get(url)
    soup = soupify(resp)
    
    print(f"--- h2 tags for '{query}' ---")
    for h2 in soup.find_all("h2", class_="entry-title"):
        a = h2.find("a", href=True)
        if a:
            print(f"- Title: {h2.get_text().strip()}")
            print(f"  URL: {a['href']}")

if __name__ == "__main__":
    inspect_h2("Inverted Back")
