
import json
import requests

from interface.basic.logger import Logging
from interface.wireless.wifi import WifiManager


def make_query(params):
    if isinstance(params, dict):
        return "&".join([f"{key}={make_query(value)}" for key, value in params.items()])
    elif isinstance(params, list):
        return ",".join(params)
    else:
        return str(params)


class API:
    def __init__(self, url: str, key: str = None, wifi: WifiManager | None = None,
                 name: str | None = None, is_logging: bool | None = None, style: str | None = None):
        self.url = url
        self.key = key
        if wifi is not None:
            self.wifi = wifi
        self.logging = Logging(name, is_logging, self, style=style)

    def request(self, endpoint: str = "", query: str | dict[str, str] = "",
                method: str = "GET", data: bytes | dict | None = None) -> requests.Response | None:
        if hasattr(self, "wifi") and not self.wifi.connected:
            return None
        data = None if data is None else data if isinstance(data, bytes) else json.dumps(data).encode("utf-8")
        query = make_query(query)
        url = f"{self.url}{'/' if endpoint else ''}{endpoint}{'?' if query else ''}{query}"
        self.logging(f"Request ({method}): {url}", "INFO")
        return requests.request(method, url, data=data)

    def get(self, endpoint: str = "", query: str | dict[str, str] = "", data: bytes | dict | None = None) -> requests.Response:
        return self.request(method="GET", endpoint=endpoint, query=query, data=data)

    def post(self, endpoint: str = "", query: str | dict[str, str] = "", data: bytes | dict | None = None) -> requests.Response:
        return self.request(method="POST", endpoint=endpoint, query=query, data=data)

    def put(self, endpoint: str = "", query: str | dict[str, str] = "", data: bytes | dict | None = None) -> requests.Response:
        return self.request(method="PUT", endpoint=endpoint, query=query, data=data)

    def patch(self, endpoint: str = "", query: str | dict[str, str] = "", data: bytes | dict | None = None) -> requests.Response:
        return self.request(method="PATCH", endpoint=endpoint, query=query, data=data)

    def delete(self, endpoint: str = "", query: str | dict[str, str] = "", data: bytes | dict | None = None) -> requests.Response:
        return self.request(method="DELETE", endpoint=endpoint, query=query, data=data)

