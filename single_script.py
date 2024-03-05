from google.cloud import speech_v1p1beta1
from google.cloud.speech_v1p1beta1.types import LongRunningRecognizeRequest, RecognitionAudio, RecognitionConfig
from google.oauth2 import service_account
import io, os

def transcribe_hindi_audio_chunked(audio_file_path=None, credentials_file_path=None, chunk_size=5242880):
    credentials = service_account.Credentials.from_service_account_file(credentials_file_path)
    client = speech_v1p1beta1.SpeechClient(credentials=credentials)
    with io.open(audio_file_path,"rb") as audio_file:
        while True:
            chunk = audio_file.read(chunk_size)
            if not chunk:
                break
            audio = {"content": chunk}
            config = {
                    "language_code": "hi-IN",
                    "enable_automatic_punctuation": True,
                    }
            response = client.recognize(config=config,audio=audio)
            for result in response.results:
                print("Transcript: {}".format(result.alternatives[0].transcript))

def transcribe_hindi_audio_long_running(audio_file_path=None, credentials_file_path=None, chunk_size=5242880):
    credentials = service_account.Credentials.from_service_account_file(credentials_file_path)
    client = speech_v1p1beta1.SpeechClient(credentials=credentials)
    with io.open(audio_file_path,"rb") as audio_file:
        audio = RecognitionAudio(uri=f"gs://rec-audio1/NAVGRAH_HOMA_PREP_DAY_4(CHANDRA)_PART_1.mp3")
        config = RecognitionConfig(
                encoding = speech_v1p1beta1.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
                sample_rate_hertz=16000,
                language_code="hi-IN",
                enable_automatic_punctuation=True,
        )
        operation = client.long_running_recognize(request=LongRunningRecognizeRequest(
            audio=audio,config=config)
        )
        print("Waiting for operation to complete...")
        response = operation.result(timeout = 5400)
        for result in response.results:
            for alternative in result.alternatives:
                print("{}\n".format(alternative.transcript))

def transcribe_hindi_audio_long_running_chunked(audio_file_path=None, credentials_file_path=None, chunk_size=500000):
    credentials = service_account.Credentials.from_service_account_file(credentials_file_path)
    client = speech_v1p1beta1.SpeechClient(credentials=credentials)
    with io.open(audio_file_path,"rb") as audio_file:
        content = audio_file.read()
    total_size = len(content)
    start = 0
    with io.open(audio_file_path, "rb") as audio_file:
        while start<total_size:
            end = min(start + chunk_size, total_size)
            config = RecognitionConfig(
                encoding=speech_v1p1beta1.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
                sample_rate_hertz=16000,
                language_code="hi-IN",
                enable_automatic_punctuation=True,
                enable_word_time_offsets=True  # Enable word time offsets for more granular results
            )
            try:
                chunk = audio_file.read(end - start)
            except Exception as e:
                print("Exception : {}".format(e))
            audio = RecognitionAudio(content=chunk)
            response = client.recognize(config=config, audio=audio)
            for result in response.results:
                for alternative in result.alternatives:
                    print("{}\n".format(alternative.transcript))
            start = end

if __name__ == "__main__":
    audio_file_path = r"C:\Users\vamsa\Downloads\NAVGRAH_HOMA_PREP_DAY_4(CHANDRA)_PART_1.mp3"
    credentials_file_path = r"C:\Users\vamsa\Downloads\service_account_key.json"
    transcribe_hindi_audio_long_running(audio_file_path=audio_file_path, credentials_file_path=credentials_file_path)


