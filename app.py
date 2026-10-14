import uuid
from pathlib import Path

import yt_dlp
from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = Path("downloads").resolve()
DOWNLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


@app.route("/")
def home():
    return jsonify({"message": "YT2MP3 converter API is running!"})


@app.route("/api/convert", methods=["POST"])
def convert():
    data = request.get_json(silent=True) or {}
    video_url = data.get("url", "").strip()

    if not video_url:
        return jsonify({"error": "Please provide a video URL."}), 400

    if not video_url.startswith(("https://", "http://")):
        return jsonify({"error": "Please provide a valid URL."}), 400

    job_id = uuid.uuid4().hex
    output_template = str(DOWNLOAD_FOLDER / f"{job_id}.%(ext)s")
    output_path = DOWNLOAD_FOLDER / f"{job_id}.mp3"

    options = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "noplaylist": True,
        "quiet": True,
        "noprogress": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([video_url])

        if not output_path.is_file():
            return jsonify({"error": "The MP3 file was not created."}), 500

        @after_this_request
        def cleanup(response):
            for path in DOWNLOAD_FOLDER.glob(f"{job_id}.*"):
                path.unlink(missing_ok=True)
            return response

        return send_file(
            output_path,
            as_attachment=True,
            download_name="converted-audio.mp3",
            mimetype="audio/mpeg",
        )

    except Exception:
        app.logger.exception("Conversion failed")
        for path in DOWNLOAD_FOLDER.glob(f"{job_id}.*"):
            path.unlink(missing_ok=True)
        return jsonify({
            "error": "Conversion failed. The source may be unavailable or the server may not be able to access it."
        }), 500


if __name__ == "__main__":
    app.run(debug=False)
