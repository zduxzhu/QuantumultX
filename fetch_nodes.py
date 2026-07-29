import json
import urllib.request
import sys

API_URL = "https://ip.v2too.top/api/nodes"
OUTPUT_FILE = "nodes.txt"

def main():
    try:
        req = urllib.request.Request(API_URL, headers={"User-Agent": "GitHub-Action"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching API: {e}", file=sys.stderr)
        sys.exit(1)

    # 兼容两种响应格式: {"value": [...]} 或直接数组 [...]
    if isinstance(data, list):
        nodes = data
    elif isinstance(data, dict):
        nodes = data.get("value", [])
    else:
        print(f"Unexpected API response type: {type(data)}", file=sys.stderr)
        sys.exit(1)

    if not nodes:
        print("No nodes found in API response", file=sys.stderr)
        sys.exit(1)

    lines = []
    for node in nodes:
        ip = node.get("ip", "")
        region = node.get("region", "")
        if ip and region:
            lines.append(f"{ip}#{region}")

    if not lines:
        print("No valid ip+region pairs found", file=sys.stderr)
        sys.exit(1)

    output = "\n".join(lines) + "\n"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"Wrote {len(lines)} nodes to {OUTPUT_FILE}")
    print("---")
    print(output.strip())

if __name__ == "__main__":
    main()
