# client.py – client for the marketplace returns API (stands in for ShopEasy's integration)

import requests
import os

import requests

BASE_URL = "http://localhost:8000"
TIMEOUT_SECONDS = 5
API_KEY = os.environ.get("MARKETPLACE_API_KEY", "dev-secret-key")

class ApiError(Exception):
    """Raised when the API answers with an error status code (4xx or 5xx)."""

    def __init__(self, status_code: int, detail):
        super().__init__(f"HTTP {status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail


class MarketplaceClient:
    """Wraps the REST API so other programs don't have to deal with HTTP details."""

    def __init__(self, base_url: str = BASE_URL, api_key: str = API_KEY):
        self.base_url = base_url
        self.headers = {"X-API-Key": api_key}

    def _request(self, method: str, path: str, **kwargs) -> dict:
        """Send one request; return the JSON body or raise ApiError on an error status."""
        response = requests.request(
            method, f"{self.base_url}{path}",
            headers=self.headers, timeout=TIMEOUT_SECONDS, **kwargs
        )
        if not response.ok:
            raise ApiError(response.status_code, response.json().get("detail"))
        return response.json()

    def list_returns(self, status: str | None = None, marketplace: str | None = None) -> list[dict]:
        params = {}
        if status:
            params["status"] = status
        if marketplace:
            params["marketplace"] = marketplace
        return self._request("GET", "/returns", params=params)["data"]

    def get_return(self, return_id: str) -> dict:
        return self._request("GET", f"/returns/{return_id}")

    def get_order(self, order_id: str) -> dict:
        return self._request("GET", f"/orders/{order_id}")

    def update_status(self, return_id: str, new_status: str) -> dict:
        return self._request("PATCH", f"/returns/{return_id}/status", json={"status": new_status})


def main() -> None:
    client = MarketplaceClient()

    print("1) Polling NEW returns (like ShopEasy every 15 minutes) ...")
    new_returns = client.list_returns(status="NEW")
    if not new_returns:
        print("   No NEW returns. Restart the server to reset the mock data.")
        return
    for r in new_returns:
        print(f"   {r['returnId']} | {r['marketplace']} | {r['reason']}")

    ret = new_returns[0]
    print(f"\n2) Loading order {ret['orderId']} for eligibility check ...")
    order = client.get_order(ret["orderId"])
    print(f"   ordered at {order['orderedAt']}, total {order['totalAmount']} {order['currency']}")

    print(f"\n3) Approving {ret['returnId']} ...")
    updated = client.update_status(ret["returnId"], "APPROVED")
    print(f"   new status: {updated['status']}")

    print("\n4) Trying a forbidden status change (APPROVED -> CLOSED) ...")
    try:
        client.update_status(ret["returnId"], "CLOSED")
    except ApiError as e:
        print(f"   rejected as expected: {e}")

    print("\n5) Asking for a return that does not exist ...")
    try:
        client.get_return("RET-9999")
    except ApiError as e:
        print(f"   {e}")

        print("\n6) Calling the API with a wrong API key ...")
    try:
        MarketplaceClient(api_key="wrong-key").list_returns()
    except ApiError as e:
        print(f"   {e}")


if __name__ == "__main__":
    try:
        main()
    except requests.ConnectionError:
        print("Cannot reach the API. Is the server running? (python -m uvicorn rest_api.main:app)")