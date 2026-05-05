from flask import Flask, request, jsonify
from flask_cors import CORS
from pytubefix import YouTube

app = Flask(__name__)
# Allow cross-origin requests
CORS(app)

# Disguise the server as different devices to bypass YouTube's 429 IP Block
CLIENTS = ['TV', 'IOS', 'WEB_CREATOR', 'ANDROID']

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Success", "message": "DFASTER API Engine is Running!"})

@app.route('/api/get-info', methods=['POST'])
def get_video_info():
    data = request.get_json()
    video_url = data.get('url', '').strip()

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    last_error_message = "YouTube completely blocked the server IP. Please wait a few minutes."

    # Loop through different device clients to trick YouTube and bypass 429
    for client_name in CLIENTS:
        try:
            yt = YouTube(video_url, client=client_name)
            
            response_data = {
                "title": yt.title,
                "thumbnail": yt.thumbnail_url,
                "duration": f"{yt.length} seconds",
                "formats": []
            }

            for stream in yt.streams:
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

            # If formats are found, return them immediately and stop the loop
            if len(response_data["formats"]) > 0:
                return jsonify(response_data)
                
        except Exception as e:
            last_error_message = str(e)
            # If blocked (429) or bot detected, silently continue to the next device client
            continue
            
    # If all device disguises fail, return the final error
    return jsonify({"error": f"Render IP Blocked by YouTube. Try again later. Details: {last_error_message}"}), 429

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
