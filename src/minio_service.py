import grpc
from concurrent import futures
import logging
from minio import Minio
from minio.error import S3Error
from src.config import config
import src.Minio_pb2 as Minio_pb2
import src.Minio_pb2_grpc as Minio_pb2_grpc
import io

logging.basicConfig(level=logging.DEBUG)


class MinioServiceServicer(Minio_pb2_grpc.MinioServiceServicer):
    def __init__(self, minio_client):
        super().__init__()
        self.minio_client = minio_client
        logging.info("MinioServiceServicer initialized")

    def UploadFile(self, request_iterator, context):
        bucket_name = None
        object_name = None
        data = b''

        for request in request_iterator:
            if bucket_name is None:
                bucket_name = request.bucket_name
                object_name = request.object_name
            data += request.chunk_data

        try:
            self.minio_client.put_object(
                bucket_name, object_name, io.BytesIO(data), len(data))
            return Minio_pb2.UploadFileResponse(success=True, message="File uploaded successfully")
        except S3Error as e:
            logging.error(f"S3Error in UploadFile: {str(e)}")
            return Minio_pb2.UploadFileResponse(success=False, message=str(e))

    def QueryFileContent(self, request, context):
        try:
            response = self.minio_client.get_object(
                request.bucket_name, request.object_name)
            if request.offset > 0:
                response.read(request.offset)
            if request.length > 0:
                content = response.read(request.length)
            else:
                content = response.read()
            return Minio_pb2.QueryFileContentResponse(content=content)
        except S3Error as e:
            logging.error(f"S3Error in QueryFileContent: {str(e)}")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return Minio_pb2.QueryFileContentResponse()

    def ListDirectory(self, request, context):
        logging.info(
            f"ListDirectory called with bucket: {request.bucket_name}, prefix: {request.prefix}")
        try:
            objects = self.minio_client.list_objects(
                request.bucket_name, prefix=request.prefix, recursive=request.recursive)
            return Minio_pb2.ListDirectoryResponse(
                files=[Minio_pb2.FileInfo(
                    name=obj.object_name,
                    is_directory=obj.object_name.endswith('/'),
                    size=obj.size,
                    last_modified=obj.last_modified.isoformat()
                ) for obj in objects]
            )
        except S3Error as e:
            logging.error(f"S3Error in ListDirectory: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"S3Error: {str(e)}")
            return Minio_pb2.ListDirectoryResponse()

    def DeleteFileOrDirectory(self, request, context):
        try:
            if request.recursive:
                objects = self.minio_client.list_objects(
                    request.bucket_name, prefix=request.path, recursive=True)
                for obj in objects:
                    self.minio_client.remove_object(
                        request.bucket_name, obj.object_name)
            else:
                self.minio_client.remove_object(
                    request.bucket_name, request.path)
            return Minio_pb2.DeleteFileOrDirectoryResponse(success=True, message="Delete operation successful")
        except S3Error as e:
            logging.error(f"S3Error in DeleteFileOrDirectory: {str(e)}")
            return Minio_pb2.DeleteFileOrDirectoryResponse(success=False, message=str(e))


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    minio_client = Minio(
        config.MINIO_ENDPOINT,
        access_key=config.MINIO_ACCESS_KEY,
        secret_key=config.MINIO_SECRET_KEY,
        secure=config.MINIO_SECURE
    )
    minio_service = MinioServiceServicer(minio_client)
    Minio_pb2_grpc.add_MinioServiceServicer_to_server(minio_service, server)
    server.add_insecure_port(
        f'{config.GRPC_SERVER_HOST}:{config.GRPC_SERVER_PORT}')
    server.start()
    logging.info(
        f"Server started on {config.GRPC_SERVER_HOST}:{config.GRPC_SERVER_PORT}")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
