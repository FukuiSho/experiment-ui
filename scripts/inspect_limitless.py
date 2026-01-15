import json

try:
    with open(r'c:\Users\ok220109\experiment-ui\src\lib\pesonaldata\unlabeldata\limitless\lifelogs.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(r'c:\Users\ok220109\experiment-ui\inspection_result.txt', 'w', encoding='utf-8') as out:
        for item in data[:2]: # Check first 2 logs
            out.write(f"--- Log ID: {item.get('id')} ---\n")
            if item.get('contents'):
                for c in item['contents'][:20]: # Check first 20 blocks
                    out.write(f"Type: {c.get('type')}, Content: {c.get('content')}\n")
            else:
                 out.write("(No contents)\n")
            out.write("\n")

except Exception as e:
    print(e)
