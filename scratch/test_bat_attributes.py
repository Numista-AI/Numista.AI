import sys
sys.path.append("c:/Users/ericd/Documents/MyVertexProject/numista_backend")
from botasaurus.request import request, Request
from botasaurus.soupify import soupify

@request
def inspect_bat_attributes(request: Request, data=None):
    url = "https://coinweek.com/grab-the-tinfoil-people-on-the-internet-are-going-batshit-over-2020-samoa-atb-quarter/"
    resp = request.get(url)
    soup = soupify(resp)
    
    print("\n--- IMG ATTRIBUTES ---")
    for img in soup.find_all("img"):
        print(f"Attributes: {list(img.attrs.keys())}")
        for k, v in img.attrs.items():
            if "http" in str(v):
                print(f"  {k}: {v}")

if __name__ == "__main__":
    inspect_bat_attributes()
