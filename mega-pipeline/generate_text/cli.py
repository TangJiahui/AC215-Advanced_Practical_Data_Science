"""
Module that contains the command line app.
"""
import argparse
import os
from google.cloud import storage
import tensorflow
# Transformers
from transformers import BertTokenizer, TFBertForSequenceClassification, BertConfig
from transformers import GPT2Tokenizer, TFGPT2LMHeadModel, GPT2Config


gcp_project = "ac215-project"
bucket_name = "mega-pipeline-bucket"
text_prompts = "text_prompts"
text_paragraphs = "text_paragraphs"

def download():
    # Initiate Storage client
    storage_client = storage.Client(project=gcp_project)

    # Get reference to bucket
    bucket = storage_client.bucket(bucket_name)

    # Find all content in a bucket
    blobs = bucket.list_blobs(prefix=f'{text_prompts}/')
    if not os.path.exists(text_prompts):
        os.mkdir(text_prompts)
    for blob in blobs:
        print(blob.name)
        if not blob.name.endswith("/"):
            blob.download_to_filename(blob.name)


def generate():
    if not os.path.exists(text_paragraphs):
        os.mkdir(text_paragraphs)

    # Tokenizer - Load the tokenizer specific to gpt2 training
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

    # Model - Load pretrained GPT Language Model
    model = TFGPT2LMHeadModel.from_pretrained("gpt2", pad_token_id=tokenizer.eos_token_id)

    if not os.path.exists(text_paragraphs):
        os.mkdir(text_paragraphs)
    for filename in os.listdir(text_prompts):
        with open(os.path.join(text_prompts,filename), "rb") as in_file:
            # Input text
            input_text = in_file.read().decode('utf-8')

            # Tokenize Input
            input_ids = tokenizer.encode(input_text, return_tensors='tf')

            # max_length is the maximum length of the whole text, including input words and generated ones.
            outputs = model.generate(input_ids, max_length=50,num_return_sequences=1)

        with open(os.path.join(text_paragraphs, filename), "wb") as out_file:
            out_file.write(outputs.text.encode())
    print("generate finished")


def upload():
    # Initiate Storage client
    storage_client = storage.Client(project=gcp_project)

    # Get reference to bucket
    bucket = storage_client.bucket(bucket_name)

    for filename in os.listdir(text_paragraphs):
        blob = bucket.blob(os.path.join(text_paragraphs, filename))
        blob.upload_from_filename(os.path.join(text_paragraphs, filename))
    print("upload finished")

def main(args=None):

    print("Args:", args)

    if args.download:
        download()
    if args.generate:
        generate()
    if args.upload:
        upload()


if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal 'python cli.py --help', it will provide the description
    parser = argparse.ArgumentParser(
        description='Generate text from prompt')

    parser.add_argument("-d", "--download", action='store_true',
                        help="Download text prompts from GCS bucket")

    parser.add_argument("-g", "--generate", action='store_true',
                        help="Generate a text paragraph")

    parser.add_argument("-u", "--upload", action='store_true',
                        help="Upload paragraph text to GCS bucket")

    args = parser.parse_args()

    main(args)