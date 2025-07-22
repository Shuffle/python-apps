FROM shuffle/shuffle:app_sdk

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY src /app
WORKDIR /app
