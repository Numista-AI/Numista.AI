import requests
import json

url = "http://localhost:5000/add-to-collection"
data = {
    "year": "1891",
    "country": "United States",
    "mint": "P",
    "grade": "MS-65",
    "file_slug": "1891_Morgan_Dollar",
    "report": "Test report for Morgan Dollar"
}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
