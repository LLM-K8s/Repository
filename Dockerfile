FROM python:3.11-alpine3.19 AS build

WORKDIR /app

COPY ../requirements.txt .

RUN apk update && apk upgrade && \
    apk add --no-cache bash && \
    pip install --no-cache-dir -r requirements.txt

COPY ../protos/ ./protos/
COPY ../script/ ./script/
COPY ../src/ ./src/

RUN chmod +x script/generate_grpc_code.sh && \
    bash script/generate_grpc_code.sh


FROM python:3.11-alpine3.19

WORKDIR /app

COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=build /app/src /app/src

EXPOSE 50051

CMD ["python", "-B", "-m", "src.main"]