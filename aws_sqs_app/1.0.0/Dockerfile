FROM shuffle/shuffle:app_sdk

WORKDIR /app
COPY src/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src/app.py .
CMD [ "python", "-u", "app.py" ]