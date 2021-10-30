"""
Module that contains the command line app.
"""
import argparse
import os
from google.cloud import storage
from tempfile import TemporaryDirectory
from google.cloud import speech
import ffmpeg
import io

gcp_project = "ac215-project"
bucket_name = "mega-pipeline-bucket"
input_audios = "input_audios"
text_prompts = "text_prompts"

def download():
    storage_client = storage.Client(gcp_project)
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=input_audios)
    if not os.path.exists(input_audios):
        os.mkdir(input_audios)
    for blob in blobs:
        if not blob.name.endswith(".mp3"):
            continue
        print(blob.name)
        blob.download_to_filename(blob.name) 
    print("download finished")


def transcribe():
    if not os.path.exists(text_prompts):
        os.mkdir(text_prompts)
    client = speech.SpeechClient()
    for filename in os.listdir(input_audios):
        audio_path = os.path.join(input_audios, filename)
        with TemporaryDirectory() as audio_dir:
            flac_path = os.path.join(audio_dir, "audio.flac")
            stream = ffmpeg.input(audio_path)
            stream = ffmpeg.output(stream, flac_path)
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)

            with io.open(flac_path, "rb") as audio_file:
                content = audio_file.read()

            # Transcribe
            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                language_code="en-US"
            )
            operation = client.long_running_recognize(
                config=config, audio=audio)
            response = operation.result(timeout=90)
            for result in response.results:
                with open(os.path.join(text_prompts, filename.replace('.mp3', '.txt')), "wb") as out_file:
                    out_file.write(result.alternatives[0].transcript.encode())
    print("transcribe finished")

def upload():
    storage_client = storage.Client(gcp_project)
    bucket = storage_client.get_bucket(bucket_name)
    for filename in os.listdir(text_prompts):
        blob = bucket.blob(os.path.join(text_prompts, filename))
        blob.upload_from_filename(os.path.join(text_prompts, filename))
    print("upload finished")

def main(args=None):
    print("Args:", args)

    if args.download:
        download()
    if args.transcribe:
        transcribe()
    if args.upload:
        upload()

if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal 'python cli.py --help', it will provide the description
    parser = argparse.ArgumentParser(
        description='Transcribe audio file to text')

    parser.add_argument("-d", "--download", action='store_true',
                        help="Download audio files from GCS bucket")

    parser.add_argument("-t", "--transcribe", action='store_true',
                        help="Transcribe audio files to text")

    parser.add_argument("-u", "--upload", action='store_true',
                        help="Upload transcribed text to GCS bucket")

    args = parser.parse_args()

    main(args)
