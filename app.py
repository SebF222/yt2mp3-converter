
import uuid
import subprocess
from pathlib import Path

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

DOWNLOAD_FOLDER = Path("downloads").resolve()
DOWNLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".mp4", ".mov", ".mkv", ".webm", ".avi",
    ".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"
}


@app.route("/")
def home():
    return jsonify({"message": "YT2MP3 converter API is running!"})


@app.route("/api/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return jsonify({
            "error": "Please upload an audio or video file."
        }), 400

    uploaded_file = request.files["file"]

    if not uploaded_file.filename:
        return jsonify({"error": "Please select a file."}), 400

    safe_name = secure_filename(uploaded_file.filename)
    extension = Path(safe_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Unsupported file type."}), 400

    job_id = uuid.uuid4().hex
    input_path = DOWNLOAD_FOLDER / f"{job_id}{extension}"
    output_path = DOWNLOAD_FOLDER / f"{job_id}.mp3"

    try:
        uploaded_file.save(input_path)

        result = subprocess.run(
            [
                "ffmpeg", "-nostdin",
                "-hide_banner", "-loglevel", "error",
                "-i", str(input_path),
                "-vn",
                "-codec:a", "libmp3lame",
                "-b:a", "192k",
                "-y", str(output_path),
            ],
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )

        if result.returncode != 0 or not output_path.is_file():
            app.logger.error("FFmpeg error: %s", result.stderr[-2000:])
            return jsonify({"error": "Could not convert this file."}), 422

        return send_file(
            output_path,
            as_attachment=True,
            download_name=f"{Path(safe_name).stem or 'audio'}.mp3",
            mimetype="audio/mpeg",
        )

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Conversion timed out."}), 408

    except Exception:
        app.logger.exception("Conversion failed")
        return jsonify({"error": "Conversion failed on the server."}), 500

    finally:
        input_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({"error": "Maximum upload size is 100 MB."}), 413


if __name__ == "__main__":
    app.run(debug=False)
