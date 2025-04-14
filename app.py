from flask import Flask, render_template, request
import pandas as pd
import os
import requests

app = Flask(__name__)

# Load your CSV or Excel data here
df = pd.read_csv('your_data.csv')  # <-- Replace with your actual file

# URL to hosted image index
IMAGE_INDEX_URL = "https://www.johnsonkeast.com/images/index.json"

# Set up a simple User-Agent header to bypass ModSecurity blocks
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []

    # Try fetching the remote index.json
    try:
        image_index = requests.get(IMAGE_INDEX_URL, headers=HEADERS).json()
    except Exception as e:
        print("⚠️ Could not load image index:", e)
        image_index = {}

    if request.method == 'POST':
        query = request.form.get('query', '').lower()
        if query:
            filtered = df[df.apply(
                lambda row: row.astype(str).str.lower().str.contains(query).any(),
                axis=1
            )]

            for _, row in filtered.iterrows():
                folder = str(row.get('Images_Folder', '')).strip()
                images = []

                # Match folder name in JSON and build image URLs
                if folder in image_index:
                    images = [
                        f"https://www.johnsonkeast.com/images/{folder}/{filename}"
                        for filename in image_index[folder]
                    ]

                results.append({
                    'data': row.to_dict(),
                    'images': images
                })

    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run
