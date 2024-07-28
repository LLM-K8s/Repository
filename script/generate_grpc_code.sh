#!/bin/bash

PROTO_DIR="./protos"
CLIENT_DIR="./client"
SERVER_DIR="./src"

mkdir -p $CLIENT_DIR $SERVER_DIR

generate_grpc_code() {
    local output_dir=$1
    echo "Generating gRPC code in $output_dir..."
    for proto_file in $PROTO_DIR/*.proto; do
        python -m grpc_tools.protoc -I$PROTO_DIR --python_out=$output_dir --grpc_python_out=$output_dir $proto_file
    done
}

modify_import() {
    local dir=$1
    echo "Modifying import statements in $dir..."
    for grpc_file in $dir/*_pb2_grpc.py; do
        base_name=$(basename "$grpc_file" _pb2_grpc.py)
        sed -i "s/import ${base_name}_pb2 as ${base_name}__pb2/import src.${base_name}_pb2 as ${base_name}__pb2/" "$grpc_file"
    done
}

generate_grpc_code $CLIENT_DIR

generate_grpc_code $SERVER_DIR
modify_import $SERVER_DIR

echo "gRPC code generation completed for both client and server."
echo "Import statements modified only in server directory."