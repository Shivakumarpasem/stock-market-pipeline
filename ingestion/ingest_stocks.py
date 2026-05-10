import yfinance as yf
import json
import os
from datetime import datetime
from azure.storage.blob import BlobServiceClient

# Configuration
STORAGE_ACCOUNT_NAME = "stockmarketdata2026"
STORAGE_ACCOUNT_KEY = "Your Storage Account KEY"  # we will fill this in a moment
BRONZE_CONTAINER = "bronze"

STOCKS = ["AAPL", "GOOGL", "MSFT", "AMZN"]

def get_stock_data(symbol):
    ticker = yf.Ticker(symbol)
    stock = ticker.history(period="1d", interval="1m")
    stock = stock.reset_index()
    stock['Datetime'] = stock['Datetime'].astype(str)
    stock['Symbol'] = symbol
    stock.columns = [col.replace(' ', '_') for col in stock.columns]
    return stock.to_dict(orient='records')

def upload_to_bronze(data, symbol):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"stocks/{symbol}/{symbol}_{timestamp}.json"
    
    connection_string = f"DefaultEndpointsProtocol=https;AccountName={STORAGE_ACCOUNT_NAME};AccountKey={STORAGE_ACCOUNT_KEY};EndpointSuffix=core.windows.net"
    
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(
        container=BRONZE_CONTAINER,
        blob=file_name
    )
    
    blob_client.upload_blob(json.dumps(data), overwrite=True)
    print(f"Uploaded {file_name} to Bronze container")

def main():
    for symbol in STOCKS:
        print(f"Fetching data for {symbol}...")
        data = get_stock_data(symbol)
        upload_to_bronze(data, symbol)
        print(f"Done: {symbol}")

if __name__ == "__main__":
    main()