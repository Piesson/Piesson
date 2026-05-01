import unittest
from tests.conftest import fake_http_response


class SmokeTest(unittest.TestCase):
    def test_helper_returns_status(self):
        r = fake_http_response(200, {"ok": True})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"ok": True})


if __name__ == "__main__":
    unittest.main()
