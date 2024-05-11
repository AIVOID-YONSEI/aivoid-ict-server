from audioseal import AudioSeal
import torch
from base64 import b64decode
from scipy.io.wavfile import read as wav_read
from scipy.io.wavfile import write as wav_write
import ffmpeg
import io
import time
import math
from google.cloud import storage

from libs.upload_gcs import upload_gcs


class WatermarkService:
    CONSTANT = 32768.0

    def __get_audio__(self, audio: str) -> tuple[any, int]:
        binary = b64decode(audio)
        process = (
            ffmpeg.input("pipe:0")
            .output("pipe:1", format="wav")
            .run_async(
                pipe_stdin=True,
                pipe_stdout=True,
                pipe_stderr=True,
                quiet=True,
                overwrite_output=True,
            )
        )
        output, _ = process.communicate(input=binary)

        riff_chunk_size = len(output) - 8

        q = riff_chunk_size
        b = []
        for _ in range(4):
            q, r = divmod(q, 256)
            b.append(r)

        riff = output[:4] + bytes(b) + output[8:]

        simple_rate, recorded = wav_read(io.BytesIO(riff))
        return recorded, simple_rate

    def generate_watermarked_audio(self, audio: str) -> str:
        recorded, sr = self.__get_audio__(audio)
        model = AudioSeal.load_generator("audioseal_wm_16bits")
        tmp = torch.tensor(recorded).float() / self.CONSTANT
        tmp = tmp.unsqueeze(0).unsqueeze(0)
        watermark = model.get_watermark(tmp, sample_rate=sr)
        watermarked_audio = tmp + watermark
        # Convert watermarked audio to audio file
        watermarked_audio = watermarked_audio.squeeze().detach().numpy() * self.CONSTANT
        watermarked_audio = watermarked_audio.astype("int16")
        # Generate a unique output file name
        # NOTE: Google App Engine: tmp에 작성하는 것만 허용
        output_file = f"/tmp/watermarked_audio_{math.ceil(time.time())}.wav"
        wav_write(output_file, sr, watermarked_audio)
        url = upload_gcs(output_file)
        return url

    def detect(self, audio: str) -> bool:
        recorded, sr = self.__get_audio__(audio)
        tmp = torch.tensor(recorded).float() / self.CONSTANT
        tmp = tmp.unsqueeze(0).unsqueeze(0)
        detector = AudioSeal.load_detector("audioseal_detector_16bits")
        result, _ = detector.detect_watermark(
            tmp, sample_rate=sr, message_threshold=0.5
        )
        return result >= 0.5
