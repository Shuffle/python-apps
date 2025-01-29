FROM python:3.10-slim

# Install all alpine build tools needed for our pip installs
RUN apt update 
RUN apt install -y clang g++ make automake autoconf libtool cmake 

# Install all of our pip packages in a single directory that we can copy to our base image later
RUN mkdir /install
WORKDIR /install

# Switch back to our base image and copy in all of our built packages and source code
#COPY --from=builder /install /usr/local
COPY src /app
COPY requirements.txt /requirements.txt
RUN python3 -m pip install -r /requirements.txt

# Install any binary dependencies needed in our final image
# RUN apk --no-cache add --update my_binary_dependency
#RUN apk --no-cache add jq git curl
RUN apt install -y jq git curl

ENV SHELL=/bin/bash

### Install Tesseract
ENV CC /usr/bin/clang
ENV CXX /usr/bin/clang++
ENV LANG=C.UTF-8
ENV TESSDATA_PREFIX=/usr/local/share/tessdata

# Dev tools
WORKDIR /tmp
#RUN apk update 
#RUN apk upgrade 

## Install the same packages with apt as with apk, but ensure they exist in apt
RUN apt install -y file openssl bash tini libpng-dev aspell-en
RUN apt install -y git clang g++ make automake autoconf libtool cmake 
RUN apt install -y autoconf-archive wget

RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

#RUN apk add tesseract-ocr  
RUN apt install -y tesseract-ocr
#RUN apk add poppler-utils 
RUN apt install -y poppler-utils
RUN apt clean && rm -rf /var/lib/apt/lists/*

# Install from main 
RUN mkdir /usr/local/share/tessdata 
RUN wget https://github.com/tesseract-ocr/tessdata_fast/raw/main/eng.traineddata -P /usr/local/share/tessdata 

RUN mkdir src 
RUN cd src 

RUN git clone --depth 1 https://github.com/tesseract-ocr/tesseract.git 

#RUN curl -fsSL https://ollama.com/install.sh | sh
# Install to /usr/local
RUN wget https://ollama.com/install.sh -O /usr/local/bin/ollama-install
RUN chmod +x /usr/local/bin/ollama-install
RUN ls /usr/local/bin
RUN sh /usr/local/bin/ollama-install

RUN ls -alh /usr/bin
RUN which ollama

#RUN /usr/local/bin/ollama pull llama3.2
RUN ollama serve & sleep 2 && ollama pull nezahatkorkmaz/deepseek-v3

#RUN rm /usr/local/bin/ollama
#RUN cd tesseract && ./autogen.sh && ./configure --build=x86_64-alpine-linux-musl --host=x86_64-alpine-linux-musl && make && make install && cd /tmp/src

# Finally, lets run our app!
WORKDIR /app
CMD ["python", "app.py", "--log-level", "DEBUG"]
