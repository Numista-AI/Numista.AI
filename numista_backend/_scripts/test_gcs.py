# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
from google.cloud import storage

def list_bucket():
    client = storage.Client()
    bucket = client.bucket('numista-training-docs')
    blobs = bucket.list_blobs(prefix='Numista.AI Training Data/US Mint Coin Programs/')
    for blob in blobs:
        print(blob.name)

if __name__ == '__main__':
    list_bucket()
