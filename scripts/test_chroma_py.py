import chromadb
try:
    client = chromadb.HttpClient(host='localhost', port=8000)
    print("Heartbeat:", client.heartbeat())
    print("Collections:", client.list_collections())
except Exception as e:
    print("Error:", e)
