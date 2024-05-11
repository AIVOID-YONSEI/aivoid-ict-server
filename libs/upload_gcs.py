from google.cloud import storage
from google.oauth2 import service_account


def upload_gcs(file_path: str) -> str:
    bucket_name = "axiomatic-robot-423003-b8.appspot.com"

    credentials = service_account.Credentials.from_service_account_file(
        "./libs/upload_gcs.json"
    )

    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    blob.upload_from_filename(filename=file_path, predefined_acl="public-read")

    return blob.public_url
