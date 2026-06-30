import urllib.parse
from botasaurus.request import request, Request
from botasaurus.soupify import soupify

@request
def inspect_search_results(request: Request, query):
    url = f"https://www.error-ref.com/?s={urllib.parse.quote_plus(query)}"
    print(f"URL: {url}")
    resp = request.get(url)
    soup = soupify(resp)
    
    # Print elements that could be search results
    print("--- h2 tags ---")
    for h2 in soup.find_all("h2"):
        print(f"h2: {h2.get_text().strip()}")
        a = h2.find("a", href=True)
        if a:
            print(f"  a: {a['href']}")
            
    print("--- post / entry classes ---")
    for div in soup.find_all(class_=lambda c: c and any(x in c.lower() for x in ["post", "entry", "content", "result"])):
        print(f"div class: {div.get('class')}")
        a = div.find("a", href=True)
        if a:
            print(f"  First link: {a.get_text().strip()} - {a['href']}")

if __name__ == "__main__":
    inspect_search_results("die gouge")
