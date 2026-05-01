import unittest
from unittest.mock import patch
from tests.conftest import fake_http_response

from _graphql_client import post_graphql, ErrorKind


class PostGraphqlClassifiesErrors(unittest.TestCase):
    URL = "https://api.github.com/graphql"
    HEADERS = {"Authorization": "Bearer x", "Content-Type": "application/json"}
    BODY = {"query": "query { viewer { login } }"}

    def test_success_returns_data(self):
        with patch("_graphql_client.requests.post",
                   return_value=fake_http_response(200, {"data": {"viewer": {"login": "Piesson"}}})):
            data, err = post_graphql(self.URL, self.HEADERS, self.BODY)
        self.assertIsNone(err)
        self.assertEqual(data["data"]["viewer"]["login"], "Piesson")

    def test_rate_limit_returns_kind(self):
        body = {"errors": [{"type": "RATE_LIMIT", "message": "..."}]}
        with patch("_graphql_client.requests.post",
                   return_value=fake_http_response(200, body)):
            data, err = post_graphql(self.URL, self.HEADERS, self.BODY)
        self.assertIsNone(data)
        self.assertEqual(err, ErrorKind.RATE_LIMIT)

    def test_http_500_returns_network(self):
        with patch("_graphql_client.requests.post",
                   return_value=fake_http_response(500, {"message": "boom"})):
            data, err = post_graphql(self.URL, self.HEADERS, self.BODY)
        self.assertIsNone(data)
        self.assertEqual(err, ErrorKind.NETWORK)

    def test_http_401_returns_auth(self):
        with patch("_graphql_client.requests.post",
                   return_value=fake_http_response(401, {"message": "Bad credentials"})):
            data, err = post_graphql(self.URL, self.HEADERS, self.BODY)
        self.assertIsNone(data)
        self.assertEqual(err, ErrorKind.AUTH)

    def test_other_graphql_error_returns_unknown(self):
        body = {"errors": [{"type": "FORBIDDEN", "message": "..."}]}
        with patch("_graphql_client.requests.post",
                   return_value=fake_http_response(200, body)):
            data, err = post_graphql(self.URL, self.HEADERS, self.BODY)
        self.assertIsNone(data)
        self.assertEqual(err, ErrorKind.UNKNOWN)

    def test_request_exception_returns_network(self):
        import requests
        with patch("_graphql_client.requests.post",
                   side_effect=requests.ConnectionError("boom")):
            data, err = post_graphql(self.URL, self.HEADERS, self.BODY)
        self.assertIsNone(data)
        self.assertEqual(err, ErrorKind.NETWORK)

    def test_http_429_returns_rate_limit(self):
        with patch("_graphql_client.requests.post",
                   return_value=fake_http_response(429, {"message": "rate limited"})):
            data, err = post_graphql(self.URL, self.HEADERS, self.BODY)
        self.assertIsNone(data)
        self.assertEqual(err, ErrorKind.RATE_LIMIT)


class PostGraphqlRetries(unittest.TestCase):
    URL = "https://api.github.com/graphql"
    HEADERS = {"Authorization": "Bearer x", "Content-Type": "application/json"}
    BODY = {"query": "query { viewer { login } }"}

    def test_retries_network_then_succeeds(self):
        from _graphql_client import post_graphql
        import requests as _r
        good = fake_http_response(200, {"data": {"ok": 1}})
        with patch("_graphql_client.requests.post",
                   side_effect=[_r.ConnectionError("blip"), good]) as p, \
             patch("_graphql_client.time.sleep"):  # don't actually sleep in tests
            data, err = post_graphql(self.URL, self.HEADERS, self.BODY)
        self.assertIsNone(err)
        self.assertEqual(data["data"]["ok"], 1)
        self.assertEqual(p.call_count, 2)

    def test_retries_5xx_max_3_times_then_gives_up(self):
        from _graphql_client import post_graphql, ErrorKind
        bad = fake_http_response(503, {"message": "down"})
        with patch("_graphql_client.requests.post", return_value=bad) as p, \
             patch("_graphql_client.time.sleep"):
            data, err = post_graphql(self.URL, self.HEADERS, self.BODY)
        self.assertIsNone(data)
        self.assertEqual(err, ErrorKind.NETWORK)
        self.assertEqual(p.call_count, 3)

    def test_does_not_retry_on_rate_limit(self):
        from _graphql_client import post_graphql, ErrorKind
        body = {"errors": [{"type": "RATE_LIMIT", "message": "..."}]}
        with patch("_graphql_client.requests.post",
                   return_value=fake_http_response(200, body)) as p, \
             patch("_graphql_client.time.sleep"):
            data, err = post_graphql(self.URL, self.HEADERS, self.BODY)
        self.assertEqual(err, ErrorKind.RATE_LIMIT)
        self.assertEqual(p.call_count, 1)

    def test_does_not_retry_on_auth(self):
        from _graphql_client import post_graphql, ErrorKind
        with patch("_graphql_client.requests.post",
                   return_value=fake_http_response(401, {"message": "Bad"})) as p, \
             patch("_graphql_client.time.sleep"):
            data, err = post_graphql(self.URL, self.HEADERS, self.BODY)
        self.assertEqual(err, ErrorKind.AUTH)
        self.assertEqual(p.call_count, 1)


if __name__ == "__main__":
    unittest.main()
