import unittest

from calclab.api import create_app
from calclab.engine import evaluate
from calclab.errors import EvalError
from calclab.history import HistoryStore
from calclab.utils import format_number


class TestHistoryStore(unittest.TestCase):
    def setUp(self):
        self.store = HistoryStore(":memory:")

    def test_recent_is_newest_first(self):
        self.store.add("1+1", "2", 2)
        self.store.add("2*3", "6", 6)
        self.assertEqual([i["expression"] for i in self.store.recent()], ["2*3", "1+1"])

    def test_variables_expose_ans(self):
        self.assertEqual(self.store.variables(), {})
        self.store.add("2*3", "6", 6)
        self.assertEqual(self.store.variables(), {"ans": 6})

    def test_clear(self):
        self.store.add("1+1", "2", 2)
        self.store.clear()
        self.assertEqual(self.store.recent(), [])


class TestVariablesAndHelpers(unittest.TestCase):
    def test_ans_variable(self):
        self.assertEqual(evaluate("ans * 2", variables={"ans": 21}), 42)

    def test_unknown_variable_still_errors(self):
        with self.assertRaises(EvalError):
            evaluate("ans + 1")

    def test_statistics_helpers(self):
        self.assertEqual(evaluate("max(1, 5, 3)"), 5)
        self.assertEqual(evaluate("min(4, 2)"), 2)
        self.assertEqual(evaluate("round(3.14159, 2)"), 3.14)
        self.assertEqual(evaluate("avg(2, 4, 6)"), 4)

    def test_avg_needs_arguments(self):
        with self.assertRaises(EvalError):
            evaluate("avg()")


class TestGroupedFormatting(unittest.TestCase):
    def test_thousands_separator(self):
        self.assertEqual(format_number(1234567, group=True), "1,234,567")
        self.assertEqual(format_number(1234.5, group=True), "1,234.5")
        self.assertEqual(format_number(1234567), "1234567")


class TestHistoryApi(unittest.TestCase):
    def setUp(self):
        self.client = create_app(db_path=":memory:").test_client()

    def post(self, expression):
        return self.client.post("/api/evaluate", json={"expression": expression}).get_json()

    def test_history_is_listed_with_grouping(self):
        self.post("1000 * 1234")
        items = self.client.get("/api/history").get_json()["items"]
        self.assertEqual(items[0]["expression"], "1000 * 1234")
        self.assertEqual(items[0]["display"], "1,234,000")

    def test_ans_chains_calculations(self):
        self.post("2 + 3")
        self.assertEqual(self.post("ans * 10")["result"], 50)

    def test_clear_history(self):
        self.post("1 + 1")
        self.client.delete("/api/history")
        self.assertEqual(self.client.get("/api/history").get_json()["items"], [])


if __name__ == "__main__":
    unittest.main()
