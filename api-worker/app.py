from flask import Flask, request, jsonify
import requests
import concurrent.futures

app = Flask(__name__)

@app.route('/fetch_data', methods=['GET'])
def fetch_data():
    keyword = request.args.get('keyword')
    if not keyword:
        return jsonify({"error": "keyword is required"}), 400

    base_url = "https://forumscout.app/api/"
    headers = {
        "X-API-Key": "29469dadb19de6b4eb0aaa3fcc5fcbf6f3a77d2c71f945c75e66a6f5532da92c",
        "Content-Type": "application/json",
    }

    endpoints = {
        "forum": {
            "url": f"{base_url}forum_search",
            "params": {"keyword": keyword, "time": "day", "page": 1},
        },
        "linkedin": {
            "url": f"{base_url}linkedin_search",
            "params": {"keyword": keyword, "page": 1, "sort_by": "date_posted"},
        },
        "reddit": {
            "url": f"{base_url}reddit_posts_search",
            "params": {"keyword": keyword, "page": 1, "sort_by": "new"},
        },
        "x": {
            "url": f"{base_url}x_search",
            "params": {"keyword": keyword, "page": 1, "sort_by": "Latest"},
        },
    }

    def get_data(name, config):
        try:
            response = requests.get(config["url"], headers=headers, params=config["params"], timeout=20)
            response.raise_for_status()
            return name, response.json()
        except Exception as e:
            return name, {"error": str(e)}

    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(get_data, k, v) for k, v in endpoints.items()]
        for f in concurrent.futures.as_completed(futures):
            name, result = f.result()
            results[name] = result

    return jsonify(results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
