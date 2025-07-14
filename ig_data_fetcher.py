import requests
import pandas as pd
import datetime

class IGClient:
    def __init__(self, api_key, username, password, demo=True):
        self.api_key = api_key
        self.username = username
        self.password = password
        self.demo = demo
        self.session = requests.Session()
        self.base_url = "https://demo-api.ig.com/gateway/deal" if demo else "https://api.ig.com/gateway/deal"
        self.authenticated = False
        self.authenticate()

    def authenticate(self):
        headers = {
            "X-IG-API-KEY": self.api_key,
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json; charset=UTF-8",
        }
        data = {
            "identifier": self.username,
            "password": self.password
        }
        response = self.session.post(f"{self.base_url}/session", json=data, headers=headers)
        response.raise_for_status()
        # Extract tokens and update session headers
        self.session.headers.update({
            "X-IG-API-KEY": self.api_key,
            "CST": response.headers.get("CST"),
            "X-SECURITY-TOKEN": response.headers.get("X-SECURITY-TOKEN"),
            "Accept": "application/json; charset=UTF-8",
        })
        self.authenticated = True

    def fetch_historical_prices(self, epic, resolution="MINUTE_5", num_points=500):
        if not self.authenticated:
            raise Exception("Not authenticated")

        params = {
            "resolution": resolution,
            "max": num_points,
        }
        url = f"{self.base_url}/prices/{epic}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        prices = data.get("prices", [])
        records = []
        for p in prices:
            record = {
                "Date": datetime.datetime.strptime(p["snapshotTime"], "%Y-%m-%dT%H:%M:%S"),
                "Open": p.get("openPrice", {}).get("bid", None),
                "High": p.get("highPrice", {}).get("bid", None),
                "Low": p.get("lowPrice", {}).get("bid", None),
                "Close": p.get("closePrice", {}).get("bid", None),
                "Volume": p.get("lastTradedVolume", 0),
            }
            records.append(record)

        df = pd.DataFrame(records).set_index("Date").sort_index()
        return df
