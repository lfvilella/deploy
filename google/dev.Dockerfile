
FROM google/cloud-sdk:321.0.0

EXPOSE 8000
EXPOSE 8080

VOLUME /app

WORKDIR /app

RUN apt-get install -y python3-venv python-pip && pip install grpcio

CMD dev_appserver.py app.yaml --host 0.0.0.0 --port 8080 --support_datastore_emulator=true --enable_console
