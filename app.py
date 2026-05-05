from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
# Allow CORS for cross-origin requests
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Success", "message": "DFASTER Backend Engine is Running!"})

@app.route('/api/get-info', methods=['POST'])
def get_video_info():
    data = request.get_json()
    video_url = data.get('url', '')

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    # Remove tracking parameters like ?si= from the YouTube URL
    if '?si=' in video_url:
        video_url = video_url.split('?si=')[0]

    ydl_opts = {
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            
            response_data = {
                "title": info_dict.get('title', 'Unknown Title'),
                "thumbnail": info_dict.get('thumbnail', ''),
                "duration": info_dict.get('duration_string', 'Unknown'),
                "formats": []
            }

            for f in info_dict.get('formats', []):
                if f.get('filesize') or f.get('filesize_approx'):
                    size_mb = round((f.get('filesize') or f.get('filesize_approx')) / (1024 * 1024), 2)
                    response_data["formats"].append({
                        "format_id": f.get('format_id'),
                        "ext": f.get('ext'),
                        "resolution": f.get('resolution', 'Audio Only'),
                        "size": f"{size_mb} MB",
                        "url": f.get('url'),
                        "vcodec": f.get('vcodec'),
                        "acodec": f.get('acodec')
                    })

            return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
