from flask import Flask, request
from flask_cors import CORS

from services.watermark_service import WatermarkService

app = Flask(__name__)
CORS(app)


@app.get("/")
def root():
    return {
        "message": "Hello World"
    }

@app.post("/audio/watermark")
def generate_watermarked_audio():
    audio = request.form['audio'] # base64 encoded
    watermarkService = WatermarkService()
    path = watermarkService.generate_watermarked_audio(audio=audio)

    return {
        "message": "success",
        "path": path
    }

@app.post("/audio/watermark/detect")
def detect_watermarked_audio():
    audio = request.form['audio'] # base64 encoded
    watermarkService = WatermarkService()
    bool = watermarkService.detect(audio=audio)

    return {
        "message": "success",
        "result": bool
    }
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)