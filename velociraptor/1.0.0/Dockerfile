# This build will need to be tweaked, as it currently sits around 502MB
FROM frikky/shuffle:app_sdk_ubuntu as base

# Install pre-reqs
COPY requirements.txt /requirements.txt
RUN apt update && apt install -y python-is-python3 python3-pip
RUN pip install -r /requirements.txt
COPY src /app

# Finally, lets run our app!
WORKDIR /app
CMD python app.py --log-level DEBUG
