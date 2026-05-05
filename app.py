from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Allow CORS for cross-origin requests
CORS(app)

def get_youtube_id(url):
    # Extract the exact video ID from any format of YouTube link
    if 'youtu.be/' in url:
        return url.split('youtu.be/')[1].split('?')[0]
    elif 'v=' in url:
        return url.split('v=')[1].split('&')[0]
    elif 'shorts/' in url:
        return url.split('shorts/')[1].split('?')[0]
    return None

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Success", "message": "DFASTER API Engine is Running!"})

@app.route('/api/get-info', methods=['POST'])
def get_video_info():
    data = request.get_json()
    video_url = data.get('url', '').strip()

    video_id = get_youtube_id(video_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL format."}), 400

    # Using public proxy instances to completely bypass YouTube Bot Protection
    instances = [
        "https://inv.tux.pizza",
        "https://invidious.nerdvpn.de",
        "https://vid.puffyan.us",
        "https://invidious.privacydev.net"
    ]

    for instance in instances:
        try:
            api_url = f"{instance}/api/v1/videos/{video_id}"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                info = response.json()
                
                # Fetch highest quality thumbnail
                thumbnails = info.get('videoThumbnails', [])
                thumb_url = thumbnails[0]['url'] if thumbnails else ''
                for t in thumbnails:
                    if t.get('quality') == 'maxresdefault':
                        thumb_url = t.get('url')
                        break

                response_data = {
                    "title": info.get('title', 'Unknown Title'),
                    "thumbnail": thumb_url,
                    "formats": []
                }

                # 1. Process High Quality Adaptive Formats
                for f in info.get('adaptiveFormats', []):
                    size_bytes = int(f.get('clen', 0))
                    if size_bytes > 0:
                        size_mb = round(size_bytes / (1024 * 1024), 2)
                        type_info = f.get('type', '')
                        
                        is_audio = 'audio' in type_info
                        resolution = 'Audio Only' if is_audio else f.get('qualityLabel', 'Unknown')
                        
                        response_data["formats"].append({
                            "resolution": resolution,
                            "size": f"{size_mb} MB",
                            "ext": f.get('container', 'mp4'),
                            "url": f.get('url'),
                            "vcodec": 'none' if is_audio else ''
                        })
                
                # 2. Process Standard & Legacy Formats (like 3GP)
                for f in info.get('formatStreams', []):
                    resolution = f.get('qualityLabel', 'Unknown')
                    ext = f.get('container', 'mp4')
                    
                    response_data["formats"].append({
                        "resolution": resolution,
                        "size": "Fast DL", 
                        "ext": ext,
                        "url": f.get('url'),
                        "vcodec": ''
                    })

                if len(response_data["formats"]) > 0:
                    return jsonify(response_data)
                    
        except Exception as e:
            # If one proxy fails, seamlessly try the next one
            continue

    return jsonify({"error": "API Servers are currently busy. Please try again."}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
