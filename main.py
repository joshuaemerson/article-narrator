import sys
import re
import os
from newspaper import Article
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

def sanitize_filename(title: str) -> str:
    """Convert the article title into a safe filename."""
    filename = re.sub(r"[^\w\s-]", "", title)  # remove special characters
    filename = re.sub(r"\s+", "_", filename.strip())  # replace spaces with underscores
    return filename[:100] or "article"

def clean_html(raw_html: str) -> str:
    """Remove null bytes and non-printable control characters."""
    # Keep standard whitespace and printable characters only
    return "".join(ch for ch in raw_html if ch.isprintable() or ch in "\n\t ")

def fetch_article(url: str) -> Article:
    """Download and parse an article from the given URL, with cleaning."""
    try:
        article = Article(url)
        article.download()

        # Clean HTML before parsing to prevent XML errors
        article.set_html(clean_html(article.html))
        article.parse()

        return article
    except Exception as e:
        print(f"Error fetching or parsing article: {e}")
        sys.exit(1)

def save_to_file(name: str, article: Article):
    """Save the extracted article to a text file inside the 'articles' folder."""
    folder = os.path.join(os.getcwd(), "articles")
    os.makedirs(folder, exist_ok=True)

    filename = name + ".txt"
    filepath = os.path.join(folder, filename)

    content = f"{article.title}\n\n{article.text}"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Article saved to: {filepath}")

def narrate(name: str, bucket_name: str, text: str):
    """
    Convert text to speech and save the output as a mp3 file and save it in an S3 bucket
    
    :param name: Name of the article .txt file
    :param bucket_name: Name of the S3 bucket
    :param text: The contents of the article in plain text
    """
    # Create a Polly client
    polly = boto3.client('polly', region_name='us-east-1')

    # Example: Convert text to speech
    response = polly.synthesize_speech(
        Engine='standard',
        SampleRate = '8000',
        Text=text,
        TextType="text",
        OutputFormat='mp3',
        VoiceId='Joanna'
    )

    # Save the audio to a file
    with open(f'{name}.mp3', 'wb') as file:
        file.write(response['AudioStream'].read())

    print(f"Speech file saved as {name}.mp3")

    s3_client = boto3.client('s3')

    try:
        s3_client.upload_file(f"./{name}.mp3", bucket_name, f"{name}.mp3")
        print(f"Uploaded '{name}.mp3' to S3")
    except FileNotFoundError:
        print("ERROR -- The file was not found.")
    except NoCredentialsError:
        print("ERROR -- AWS credentials not found. Configure them with `aws configure`.")
    except ClientError as e:
        print(f"ERROR -- Upload failed: {e}")


def main():
    if len(sys.argv) < 2:
        print("ERROR -- expected article URL")
        sys.exit(1)

    url = sys.argv[1]
    print(f"Fetching article from: {url}")

    article = fetch_article(url)
    filename = sanitize_filename(article.title)
    save_to_file(filename, article)
    narrate(filename, "article-storage-1029384756", article.text[:1500]) # limit to 1500 characters to meet Amazon Polly constraints

if __name__ == "__main__":
    main()
