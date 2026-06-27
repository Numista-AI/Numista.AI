import os
import sys
import unittest

# Adjust path to import numista_backend
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "numista_backend"))
sys.path.insert(0, backend_path)

from fastapi.testclient import TestClient
from main import app

class TestReferenceAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_get_grade(self):
        # Test valid grade
        response = self.client.get("/api/reference/grade/AU-58")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["grade_code"], "AU-58")
        self.assertEqual(data["grade_name"], "Choice About Uncirculated")
        self.assertTrue(data["illustration_url"].startswith("https://storage.googleapis.com/"))

        # Test invalid grade
        response = self.client.get("/api/reference/grade/MS-99")
        self.assertEqual(response.status_code, 404)

    def test_get_glossary(self):
        response = self.client.get("/api/reference/glossary")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data) > 0)
        # Verify obverse is present
        terms = [item["term"] for item in data]
        self.assertIn("Obverse", terms)
        self.assertIn("Reverse", terms)

    def test_search_sqlite(self):
        # Direct term match
        response = self.client.post("/api/reference/search", json={"query": "Luster"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["matched"])
        self.assertEqual(data["source"], "sqlite")
        self.assertEqual(data["term"]["term"], "Luster")

        # Colloquial match
        response = self.client.post("/api/reference/search", json={"query": "heads"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["matched"])
        self.assertEqual(data["source"], "sqlite")
        self.assertEqual(data["term"]["term"], "Obverse")

    def test_search_gemini_fallback(self):
        # Relates to Obverse: "face of a coin"
        response = self.client.post("/api/reference/search", json={"query": "face of a coin"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        print("Gemini fallback response:", data)
        self.assertTrue(data["matched"])
        self.assertEqual(data["source"], "gemini")
        self.assertEqual(data["term"]["term"], "Obverse")

if __name__ == "__main__":
    unittest.main()
