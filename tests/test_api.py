import unittest

from calclab import __version__
from calclab.api import create_app


class TestApi(unittest.TestCase):
    def setUp(self):
        self.client = create_app(db_path=":memory:").test_client()

    def post(self, expression):
        return self.client.post("/api/evaluate", json={"expression": expression})

    def test_health(self):
        data = self.client.get("/api/health").get_json()
        self.assertEqual(data, {"status": "ok", "version": __version__})

    def test_evaluate_success(self):
        res = self.post("2 + 3 * 4")
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["ok"])
        self.assertEqual(data["result"], 14)
        self.assertEqual(data["display"], "14")

    def test_evaluate_error_is_400_with_message(self):
        res = self.post("1 / 0")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.get_json(), {"ok": False, "error": "Division by zero"})

    def test_missing_or_invalid_body(self):
        res = self.client.post("/api/evaluate", data="not json", content_type="text/plain")
        self.assertEqual(res.status_code, 400)

    def test_ui_is_served(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"CalcLab", res.data)
        res.close()
        css = self.client.get("/style.css")
        self.assertEqual(css.status_code, 200)
        css.close()


if __name__ == "__main__":
    unittest.main()
