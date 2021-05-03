# Running the project

$ docker build -f dev.Dockerfile -t gcp-sdk-local . && docker run --rm -v $(PWD):/app -w /app -p 8080:8080 -p 8000:8000 -it gcp-sdk-local dev_appserver.py app.yaml --host 0.0.0.0 --port 8080 --support_datastore_emulator=true --enable_console
