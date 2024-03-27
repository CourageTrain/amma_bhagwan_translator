import argparse
import ffmpeg
from pydub import AudioSegment
import io
import os
import logging
import time
import tkinter as tk
from tkinter import filedialog

from google.cloud import speech_v1p1beta1
from google.cloud import storage
from google.oauth2 import service_account
from google.cloud.speech_v1p1beta1 import LongRunningRecognizeRequest
from google.cloud.speech_v1p1beta1 import RecognitionAudio
from google.cloud.speech_v1p1beta1 import RecognitionConfig
from googletrans import Translator

BUCKET_NAME = "rec-audio1"
DOWNLOADS_PATH = r"C:\Users\vamsa\Downloads"
TIME_INTERVAL = 20
CREDENTIALS_PATH = r"C:\Users\vamsa\Downloads\service_account_key.json"

def browse_file():
    filename = filedialog.askopenfilename()
    audio_file_entry.delete(0, tk.END)
    audio_file_entry.insert(tk.END, filename)

def start_transcription():
    audio_file_path = audio_file_entry.get()
    upload_blob(bucket_name=BUCKET_NAME, source_file_name=audio_file_path,credentials_file_path=CREDENTIALS_PATH)
    transcribe_hindi_audio_long_running(audio_file_path=audio_file_path, credentials_file_path=CREDENTIALS_PATH)

def upload_blob(bucket_name=None, source_file_name=None, credentials_file_path=None):
    """Uploads a file to a Google Storage Bucket."""
    if bucket_name is None or source_file_name is None:
        return None
    # create a credentials object
    credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
    # create a storage client
    storage_client = storage.Client(credentials=credentials)
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
        operation = speech_client.long_running_recognize(request=LongRunningRecognizeRequest(
            audio=audio,config=config)
        )
        print("Waiting for operation to complete...")
        start_time = time.time() # Record the start time
        while not operation.done():
            curr_time = time.time()
            print(f"time taken:{curr_time-start_time} Progress:{operation.metadata.progress_percent}%")
            time.sleep(TIME_INTERVAL)
        response = operation.result(timeout=10000)
        for result in response.results:
            for alternative in result.alternatives:
                print("{}\n".format(alternative.transcript))
        for result in response.results:
            for alternative in result.alternatives:
                hindi_text = alternative.transcript
                translation = translator.translate(hindi_text, src='hi', dest='en')
                print(f"{translation.text}\n")


if __name__ == "__main__":
    root = tk.Tk()
    audio_file_label = tk.Label(root, text="Audio File")
    audio_file_label.pack()
    audio_file_entry = tk.Entry(root)
    audio_file_entry.pack()
    browse_button = tk.Button(root, text="Browse", command=browse_file)
    browse_button.pack()
    start_button = tk.Button(root, text="Start Transcription", command=start_transcription)
    start_button.pack()
    root.mainloop()
