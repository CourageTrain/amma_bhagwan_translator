import argparse
import ffmpeg
from pydub import AudioSegment
import io
import os
import logging
import time

from google.cloud import speech_v1p1beta1
from google.cloud import storage
from google.oauth2 import service_account
from google.cloud.speech_v1p1beta1 import LongRunningRecognizeRequest
from google.cloud.speech_v1p1beta1 import RecognitionAudio
from google.cloud.speech_v1p1beta1 import RecognitionConfig

BUCKET_NAME = "rec-audio1"
DOWNLOADS_PATH = r"C:\Users\vamsa\Downloads"
TIME_INTERVAL = 20
CREDENTIALS_PATH = r"C:\Users\vamsa\Downloads\service_account_key.json"

def upload_blob(bucket_name=None, source_file_name=None):
    """Uploads a file to a Google Storage Bucket."""
    if bucket_name is None or source_file_name is None:
        return None
    # create a storage client
    storage_client = storage.Client()
    # get the bucket
    bucket = storage_client.bucket(bucket_name)
    # create a blob
    blob = bucket.blob(source_file_name)
    # upload the blob to the bucket
    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {bucket_name}.")

def transcribe_hindi_audio_long_running(audio_file_path=None, credentials_file_path=None):
    if audio_file_path is None or credentials_file_path is None:
        return None
    # create a credentials object
    credentials = service_account.Credentials.from_service_account_file(credentials_file_path)
    # create a speech client
    speech_client = speech_v1p1beta1.SpeechClient(credentials=credentials)
    # create a long running recognize request
    with io.open(audio_file_path,"rb") as audio_file:
        audio = RecognitionAudio(uri=f"gs://rec-audio1/{os.path.basename(audio_file_path)}")
        config = RecognitionConfig(
                encoding = speech_v1p1beta1.RecognitionConfig.AudioEncoding.MP3,
                sample_rate_hertz=16000,
                language_code="hi-IN",
                enable_automatic_punctuation=True,
        )
        operation = client.long_running_recognize(request=LongRunningRecognizeRequest(
            audio=audio,config=config)
        )
        print("Waiting for operation to complete...")
        while not operation.done():
            print(f"Progress:{operation.metadata.progress_percent}%")
            time.sleep(TIME_INTERVAL)
        response = operation.result(timeout=10000)
        for result in response.results:
            for alternative in result.alternatives:
                print("{}\n".format(alternative.transcript))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe Hindi Audio")
    parser.add_argument("--audio_location",type=str, help="Path to Downloads directory", default=DOWNLOADS_PATH)
    parser.add_argument("--audio_file", type=str, help="Name of the audio file", default=None)
    parser.add_argument("--credentials_path", type=str, help="Path to credentials file", default=CREDENTIALS_PATH)
    args = parser.parse_args()
    upload_blob(bucket_name = BUCKET_NAME, source_file_name = args.audio_file_path)
    transcribe_hindi_audio_long_running(audio_file_path=args.audio_file_path, credentials_file_path=args.CREDENTIALS_PATH)
