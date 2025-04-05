from flask import Flask, request, jsonify, render_template
import requests
import pandas as pd
import os
import random

app = Flask(__name__)

# Replace with your YouTube API key
YOUTUBE_API_KEY = "AIzaSyClhKeiGYtvK30D6OfhRn55-llYclUX2bE"

# CSV file to store search history
CSV_FILE = "search_history.csv"

# Function to fetch trending songs (Music Category ID: 10)
def fetch_trending_songs():
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&chart=mostPopular&regionCode=US&videoCategoryId=10&maxResults=6&key={YOUTUBE_API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        return []

    data = response.json()
    results = []

    for item in data.get("items", []):
        video_id = item["id"]
        title = item["snippet"]["title"]
        description = item["snippet"]["description"]
        thumbnail = item["snippet"]["thumbnails"]["medium"]["url"]

        # Exclude Shorts
        if "shorts" not in title.lower():
            results.append({
                "videoId": video_id, 
                "title": title, 
                "description": description, 
                "thumbnail": thumbnail
            })

    random.shuffle(results)  # Shuffle trending songs
    return results

# Function to search for songs
def search_youtube(query):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query} song&type=video&videoEmbeddable=true&videoCategoryId=10&maxResults=6&key={YOUTUBE_API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        return []

    data = response.json()
    results = []

    for item in data.get("items", []):
        video_id = item["id"].get("videoId")
        title = item["snippet"]["title"]
        description = item["snippet"]["description"]
        thumbnail = item["snippet"]["thumbnails"]["medium"]["url"]

        # Exclude Shorts
        if video_id and "shorts" not in title.lower():
            results.append({
                "videoId": video_id, 
                "title": title, 
                "description": description, 
                "thumbnail": thumbnail
            })

    return results

# Function to save search history
def save_search_history(song_name, video_id, title):
    data = {"song_name": song_name, "video_id": video_id, "title": title}
    df = pd.DataFrame([data])

    if os.path.exists(CSV_FILE):
        df.to_csv(CSV_FILE, mode='a', header=False, index=False)
    else:
        df.to_csv(CSV_FILE, index=False)

# API route to search songs
@app.route("/search", methods=["GET"])
def search_song():
    song_query = request.args.get("query")
    if not song_query:
        return jsonify({"error": "No search query provided"}), 400

    song_data = search_youtube(song_query)
    random.shuffle(song_data)  # Shuffle results every time
    return jsonify(song_data)

# API to fetch related songs
@app.route("/related", methods=["GET"])
def fetch_related_songs():
    song_title = request.args.get("title")
    if not song_title:
        return jsonify({"error": "No song title provided"}), 400

    related_songs = search_youtube(song_title + " music")
    random.shuffle(related_songs)  # Shuffle related songs each time

    return jsonify(related_songs)

# Home Page
@app.route("/")
def home():
    trending_videos = fetch_trending_songs()
    return render_template("index.html", trending_videos=trending_videos)

if __name__ == "__main__":
    app.run(debug=True)
