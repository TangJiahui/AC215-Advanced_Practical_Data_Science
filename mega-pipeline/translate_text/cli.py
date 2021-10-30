"""
Module that contains the command line app.
"""
import argparse
import os
from google.cloud import storage
from googletrans import Translator

gcp_project = "ac215-project"
bucket_name = "mega-pipeline-bucket"
text_paragraphs = "text_paragraphs"
text_translated = "text_translated"

def download():
    storage_client = storage.Client(gcp_project)
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=text_paragraphs)
    if not os.path.exists(text_paragraphs):
        os.mkdir(text_paragraphs)
    for blob in blobs:
        if not blob.name.endswith(".txt"):
            continue
        print(blob.name)
        blob.download_to_filename(blob.name) 
    print("download finished")

def translate():
    translator = Translator()
    if not os.path.exists(text_translated):
        os.mkdir(text_translated)
    for filename in os.listdir(text_paragraphs):
        with open(os.path.join(text_paragraphs,filename), "rb") as in_file:
            input_text = in_file.read().decode('utf-8')
        results = translator.translate(input_text, src="en", dest="fr")
        with open(os.path.join(text_translated, filename), "wb") as out_file:
            out_file.write(results.text.encode())
    print("translate finished")

def upload():
    storage_client = storage.Client(gcp_project)
    bucket = storage_client.get_bucket(bucket_name)
    for filename in os.listdir(text_translated):
        blob = bucket.blob(os.path.join(text_translated, filename))
        blob.upload_from_filename(os.path.join(text_translated, filename))
    print("upload finished")

def main(args=None):

    print("Args:", args)

    if args.download:
        download()
    if args.translate:
        translate()
    if args.upload:
        upload()

if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal 'python cli.py --help', it will provide the description
    parser = argparse.ArgumentParser(
        description='Translate English to French')

    parser.add_argument("-d", "--download", action='store_true',
                        help="Download text paragraphs from GCS bucket")

    parser.add_argument("-t", "--translate", action='store_true',
                        help="Translate text")

    parser.add_argument("-u", "--upload", action='store_true',
                        help="Upload translated text to GCS bucket")

    args = parser.parse_args()

    main(args)