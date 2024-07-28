import os


class Config:
    MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT', 'MINIO_ENDPOINT')
    MINIO_ACCESS_KEY = os.environ.get(
        'MINIO_ACCESS_KEY', 'MINIO_ACCESS_KEY')
    MINIO_SECRET_KEY = os.environ.get(
        'MINIO_SECRET_KEY', 'MINIO_SECRET_KEY')
    MINIO_SECURE = os.environ.get('MINIO_SECURE', 'False').lower() == 'true'

    GRPC_SERVER_HOST = os.environ.get('GRPC_SERVER_HOST', 'GRPC_SERVER_HOST')
    GRPC_SERVER_PORT = int(os.environ.get(
        'GRPC_SERVER_PORT', 'GRPC_SERVER_PORT'))


config = Config()
