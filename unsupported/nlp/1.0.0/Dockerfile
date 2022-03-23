# Base our app image off of the WALKOFF App SDK image
FROM frikky/shuffle:app_sdk as base

# We're going to stage away all of the bloat from the build tools so lets create a builder stage
# Install all alpine build tools needed for our pip installs
FROM base as builder
RUN apk --no-cache add --update alpine-sdk libffi libffi-dev musl-dev openssl-dev

# Install all of our pip packages in a single directory that we can copy to our base image later
RUN mkdir /install
WORKDIR /install
#COPY requirements.txt /requirements.txt
#RUN pip install --prefix="/install" -r /requirements.txt
RUN pip install tika==1.24
RUN pip install requests==2.25.1
RUN pip install spacy==2.3.5
RUN pip install cyberspacy==1.1.1

# Switch back to our base image and copy in all of our built packages and source code
FROM base
COPY --from=builder /install /usr/local
COPY src /app

# Install any binary dependencies needed in our final image
# RUN apk --no-cache add --update my_binary_dependency
RUN apk add --no-cache libstdc++ openjdk8
RUN python -m spacy download en_core_web_lg
RUN python3 -c 'import tika; tika.initVM(); tika.parser.from_file('/bin/bash')'

# Finally, lets run our app!
WORKDIR /app
CMD python app.py --log-level DEBUG
