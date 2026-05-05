from flask import Flask, request, jsonify
from flask_cors import CORS
from pytubefix import YouTube

app = Flask(__name__)
# Allow CORS for cross-origin requests
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Success", "message": "DFASTER API Engine is Running flawlessly!"})

@app.route('/api/get-info', methods=['POST'])
def get_video_info():
    data = request.get_json()
    video_url = data.get('url', '').strip()

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # Using pytubefix with 'ANDROID' client to bypass YouTube Bot Protection seamlessly
        yt = YouTube(video_url, client='ANDROID')
        
        response_data = {
            "title": yt.title,
            "thumbnail": yt.thumbnail_url,
            "duration": f"{yt.length} seconds",
            "formats": []
        }

        # Extract available video and audio streams
        for stream in yt.streams:
            # We only want streams that have a calculable file size
            if stream.filesize:
                size_mb = round(stream.filesize / (1024 * 1024), 2)
                is_audio = (stream.includes_video_track == False)
                
                resolution = 'Audio Only' if is_audio else (stream.resolution or 'Unknown')
                
                response_data["formats"].append({
                    "resolution": resolution,
                    "size": f"{size_mb} MB",
                    "ext": stream.subtype,
                    "url": stream.url,
                    "vcodec": 'none' if is_audio else (stream.video_codec or '')
                })

        if len(response_data["formats"]) == 0:
            return jsonify({"error": "No formats found. Video might be protected."}), 400

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
