import os
import wave
import whisper
import time
from tempfile import NamedTemporaryFile

model = whisper.load_model("small")


def process_audio_chunk(pcm_chunks: bytearray) -> tuple[str, dict]:
    """
    Processes a chunk of audio data, transcribes it, and returns the
    transcription and performance metrics.
    """
    start_total = time.perf_counter()
    start_wav = time.perf_counter()
    with NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
        with wave.open(wav_file, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(pcm_chunks)
        tmp_filename = wav_file.name
    end_wav = time.perf_counter()

    try:
        start_transcribe = time.perf_counter()
        result = model.transcribe(tmp_filename, language="en")
        end_transcribe = time.perf_counter()
        text = result["text"].strip()
        performance = {
            "wav_write": end_wav - start_wav,
            "transcription": end_transcribe - start_transcribe,
            "total": time.perf_counter() - start_total,
        }
        return text, performance
    finally:
        os.remove(tmp_filename)
