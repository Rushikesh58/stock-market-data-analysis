import requests
import json
import pandas as pd
from datetime import datetime

def fetch_alpha_vantage_data(symbol: str, api_key: str) -> pd.DataFrame:
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses

        data = response.json()

        # Check for API error or limit exceeded
        if "Error Message" in data:
            raise ValueError(f"API returned an error: {data['Error Message']}")
        elif "Note" in data:
            raise ValueError(f"API limit reached: {data['Note']}")
        elif "Time Series (Daily)" not in data:
            raise KeyError("Missing 'Time Series (Daily)' in response")

        timeseries = data["Time Series (Daily)"]
        df = pd.DataFrame.from_dict(timeseries, orient="index")
        df = df.rename(columns={
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. volume": "Volume"
        })

        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df = df.astype(float)

        df.reset_index(inplace=True)
        df.rename(columns={"index": "DATE"}, inplace=True)

        print(f"Successfully fetched {len(df)} records for {symbol}")
        return df

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except ValueError as e:
        print(f"Value error: {e}")
    except KeyError as e:
        print(f"Unexpected data format: missing key {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return pd.DataFrame()  # Return empty DataFrame on failure

