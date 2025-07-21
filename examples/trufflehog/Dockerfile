FROM alpine:latest

WORKDIR /app

# Copy the setting file into the Docker image
COPY vulnerable_setting /app/vulnerable_setting

CMD ["cat", "/app/vulnerable_setting"]