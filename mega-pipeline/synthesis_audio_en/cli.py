"""
Module that contains the command line app.
"""
import argparse
from google.cloud import storage
from google.cloud import texttospeech
import os



gcp_project = "ac215-project"
bucket_name = "mega-pipeline-bucket"
text_paragraphs = "text_paragraphs"
text_audios = "text_audios"


def download():
    # Initiate Storage client
    storage_client = storage.Client(project=gcp_project)

    # Get reference to bucket
    bucket = storage_client.bucket(bucket_name)

    # Find all content in a bucket
    blobs = bucket.list_blobs(prefix=f'{text_paragraphs}/')

    if not os.path.exists(text_paragraphs):
        os.mkdir(text_paragraphs)
    for blob in blobs:
        print(blob.name)
        if not blob.name.endswith("/"):
            blob.download_to_filename(blob.name)
    print("download finished")


def synthesis():
    if not os.path.exists(text_audios):
        os.mkdir(text_audios)
        
    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    for filename in os.listdir(f'{text_paragraphs}/'): 
        with open(os.path.join(text_paragraphs, filename), 'r') as f:

            # Set the text input to be synthesized
            synthesis_input = texttospeech.SynthesisInput(text=f.read())

            # Build the voice request
            language_code = "en-US"
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code, ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )

            # Select the type of audio file you want returned
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            # Perform the text-to-speech request on the text input with the selected
            # voice parameters and audio file type
            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            # Save the audio file
            audio_file = filename.replace('txt', 'mp3')

            with open(os.path.join(text_audios, audio_file), "wb") as out:
                # Write the response to the output file.
                out.write(response.audio_content)
    print('synthesis_audio_en finished')

def upload():
    # Initiate Storage client
    storage_client = storage.Client(project=gcp_project)

    # Get reference to bucket
    bucket = storage_client.bucket(bucket_name)

    for filename in os.listdir(text_audios):
        blob = bucket.blob(os.path.join(text_audios, filename))
        blob.upload_from_filename(os.path.join(text_audios, filename))
    print("upload finished")


def main(args=None):

    print("Args:", args)

    if args.download:
        download()
    if args.synthesis:
        synthesis()
    if args.upload:
        upload()


if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal 'python cli.py --help', it will provide the description
    parser = argparse.ArgumentParser(
        description='Synthesis audio from text')

    parser.add_argument("-d", "--download", action='store_true',
                        help="Download paragraph of text from GCS bucket")

    parser.add_argument("-s", "--synthesis", action='store_true',
                        help="Synthesis audio")

    parser.add_argument("-u", "--upload", action='store_true',
                        help="Upload audio file to GCS bucket")

    args = parser.parse_args()

    main(args)