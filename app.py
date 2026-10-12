
import re
import uuid
from pathlib import Path

import yt_dlp
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = Path("downloads").resolve()
DOWNLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


def is_valid_url(url):
    return (
        url.startswith("https://")
        and re.match(r"^https://[a-zA-Z0-9.-]+(?::\d+)?(?:/|$)", url)
        and not any(char.isspace() for char in url)
    )


@app.route("/")
def home():
    return jsonify({"message": "YT2MP3 Converter API is running!"})


@app.route("/api/convert", methods=["POST"])
def convert():
    data = request.get_json(silent=True) or {}
    video_url = data.get("url", "").strip()

    if not is_valid_url(video_url):
        return jsonify({"error": "Please enter a valid HTTPS URL."}), 400

    job_id = uuid.uuid4().hex
    output_template = str(DOWNLOAD_FOLDER / f"{job_id}.%(ext)s")

    options = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([video_url])

        mp3_path = DOWNLOAD_FOLDER / f"{job_id}.mp3"

        if not mp3_path.is_file():
            return jsonify({"error": "The MP3 file was not created."}), 500

        return send_file(
            mp3_path,
            as_attachment=True,
            download_name="converted-audio.mp3",
            mimetype="audio/mpeg",
        )

    
    except Exception as e:
        app.logger.exception("Audio conversion failed")
        return jsonify({
            "error": f"Conversion failed: {str(e)[:300]}"
        }), 500



if __name__ == "__main__":
    app.run(debug=False)

