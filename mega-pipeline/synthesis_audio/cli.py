"""
Module that contains the command line app.
"""
import argparse
from google.cloud import storage
from google.cloud import texttospeech
import os

gcp_project = "ac215-project"
bucket_name = "mega-pipeline-bucket"
output_audios = "output_audios"
text_translated = "text_translated"

def download():
    # Initialise a client
    storage_client = storage.Client(gcp_project)
    # Create a bucket object for our bucket
    bucket = storage_client.get_bucket(bucket_name)
    # Create a blob object from the filepath
    blobs = bucket.list_blobs(prefix=text_translated)
    # Download the file to a destination
    if not os.path.exists(text_translated):
        os.mkdir(text_translated)
    for blob in blobs:
        if not blob.name.endswith(".txt"):
            continue
        print(blob.name)
        blob.download_to_filename(blob.name) 
    print("download finished")
    
def synthesis():
    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Build the voice request
    language_code = "fr-FR"
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code, ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    if not os.path.exists(output_audios):
        os.mkdir(output_audios)

    # Set the text input to be synthesized
    for filename in os.listdir(text_translated):
        with open(os.path.join(text_translated,filename), "rb") as in_file:
            input_text = in_file.read()
        synthesis_input = texttospeech.SynthesisInput(text=input_text)

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        with open(os.path.join(output_audios, filename.replace('.txt', '.mp3')), "wb") as out_file:
            # Write the response to the output file.
            out_file.write(response.audio_content)
    print("synthesis finished")

def upload():
    storage_client = storage.Client(gcp_project)
    bucket = storage_client.get_bucket(bucket_name)
    for filename in os.listdir(output_audios):
        blob = bucket.blob(os.path.join(output_audios, filename))
        blob.upload_from_filename(os.path.join(output_audios, filename))
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