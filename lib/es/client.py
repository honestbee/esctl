import sys
import time
import json
from uuid import uuid4
import requests
from retrying import retry
from urllib.parse import urljoin


def _mk_headers():
    """Generate the default headers for making requests to the ES API"""
    return {'Content-type': 'application/json'}


def _mk_auth(user=None, password=None):
    """Returns an implementation of `requests.auth.AuthBase` to authenticate with the server based
    on given options. Will return None if no auth-specific options are present"""

    if (user is not None and password is not None):
        print("Using HTTP Basic auth")
        return requests.auth.HTTPBasicAuth(user, password)
    else:
        return None


class Client:
    """Base ES client implementation"""

    def __init__(self, url, user=None, password=None):
        if url is None:
            raise Exception("Cluster URL must be provided")
        self._cluster_url = url
        self._auth = _mk_auth(user, password)


    def do_request(self, method, path, payload=None, expected=200):
        """Make a generic request"""
        headers = _mk_headers()
        data = json.dumps(payload) if payload else None
        url = self._url_from(path)

        res = requests.request(method, url, data=data, headers=headers, auth=self._auth)
        return self._validate_response(res, expected)


    def do_get(self, url, expected=200):
        """Make a GET request"""
        return self.do_request("get", url, expected=expected)


    def do_put(self, url, payload=None, expected=200):
        """Make a PUT request"""
        return self.do_request("put", url, payload=payload, expected=expected)


    def do_post(self, url, payload=None, expected=(200, 201)):
        """Make a POST request"""
        return self.do_request("post", url, payload=payload, expected=expected)


    def do_delete(self, url, expected=200):
        """Make a DELETE request"""
        return self.do_request("delete", url, expected=expected)


    def _url_from(self, path):
        """Returns full cluster url to given path"""
        return urljoin(self._cluster_url, path)


    def _validate_response(self, res, expected=(200, 201)):
        """Check if response status code is within expected values, if not raises an Exception"""

        if expected is None:
            return res
        if isinstance(expected, int):
            expected = [expected]

        if res.status_code not in expected:
            print(res.text, file=sys.stderr)
            raise Exception("Unexpected response status ("+str(res.status_code)+")")

        return res.json(), res
