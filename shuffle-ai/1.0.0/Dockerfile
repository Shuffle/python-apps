# Base our app image off of the WALKOFF App SDK image
FROM frikky/shuffle:app_sdk as base

# We're going to stage away all of the bloat from the build tools so lets create a builder stage
FROM base as builder

# Install all alpine build tools needed for our pip installs
RUN apk --no-cache add --update alpine-sdk libffi libffi-dev musl-dev openssl-dev git

# Install all of our pip packages in a single directory that we can copy to our base image later
RUN mkdir /install
WORKDIR /install

# Switch back to our base image and copy in all of our built packages and source code
FROM base
COPY --from=builder /install /usr/local
COPY src /app
COPY requirements.txt /requirements.txt
RUN python3 -m pip install -r /requirements.txt

# Install any binary dependencies needed in our final image
# RUN apk --no-cache add --update my_binary_dependency
RUN apk --no-cache add jq git curl

ENV SHELL=/bin/bash

### Install Tesseract
ENV CC /usr/bin/clang
ENV CXX /usr/bin/clang++
ENV LANG=C.UTF-8
ENV TESSDATA_PREFIX=/usr/local/share/tessdata

# Dev tools
WORKDIR /tmp
RUN apk update 
RUN apk upgrade 
RUN apk add file openssl openssl-dev bash tini leptonica-dev  openjpeg-dev tiff-dev libpng-dev zlib-dev libgcc mupdf-dev jbig2dec-dev 
RUN apk add freetype-dev openblas-dev ffmpeg-dev linux-headers aspell-dev aspell-en  # enchant-dev jasper-dev 
RUN apk add --virtual .dev-deps git clang clang-dev g++ make automake autoconf libtool pkgconfig cmake ninja 
RUN apk add --virtual .dev-testing-deps -X http://dl-3.alpinelinux.org/alpine/edge/testing autoconf-archive 
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

RUN apk add tesseract-ocr  
RUN apk add poppler-utils 

# Install from main 
RUN mkdir /usr/local/share/tessdata 
RUN mkdir src 
RUN cd src 
RUN wget https://github.com/tesseract-ocr/tessdata_fast/raw/main/eng.traineddata -P /usr/local/share/tessdata 
RUN git clone --depth 1 https://github.com/tesseract-ocr/tesseract.git 
#RUN cd tesseract && ./autogen.sh && ./configure --build=x86_64-alpine-linux-musl --host=x86_64-alpine-linux-musl && make && make install && cd /tmp/src

# Finally, lets run our app!
WORKDIR /app
CMD ["python", "app.py", "--log-level", "DEBUG"]
