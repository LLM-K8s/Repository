import grpc
from concurrent import futures
import src.Minio_pb2_grpc as Minio_pb2_grpc
from src.minio_service import MinioServiceServicer
from minio import Minio
from src.config import config


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    minio_client = Minio(
        config.MINIO_ENDPOINT,
        access_key=config.MINIO_ACCESS_KEY,
        secret_key=config.MINIO_SECRET_KEY,
        secure=config.MINIO_SECURE
    )

    Minio_pb2_grpc.add_MinioServiceServicer_to_server(
        MinioServiceServicer(minio_client), server)

    server.add_insecure_port(f'[::]:{config.GRPC_SERVER_PORT}')
    server.start()
    print(
        f"Server started on port {config.GRPC_SERVER_HOST}:{config.GRPC_SERVER_PORT}")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
