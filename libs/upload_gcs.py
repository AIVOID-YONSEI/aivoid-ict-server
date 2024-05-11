from google.cloud import storage


def upload_gcs(file_path: str) -> str:
    bucket_name = "axiomatic-robot-423003-b8.appspot.com"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    blob.upload_from_filename(file_path)

    return blob.public_url
