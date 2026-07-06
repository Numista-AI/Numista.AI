# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import urllib.request
import pandas as pd

url = "https://en.wikipedia.org/wiki/American_Innovation_dollars"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')

tables = pd.read_html(html)
# Find the coin release table
for i, df in enumerate(tables):
    col_str = " ".join(str(c) for c in df.columns)
    if "Year" in col_str and "Innovation" in col_str:
        print("Found matching table:")
        print(df.head())
        df.to_csv("wiki_data.csv", index=False)
        break
