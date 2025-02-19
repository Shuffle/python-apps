FROM python:3.10-slim

### Install Tesseract
ENV SHELL=/bin/bash
ENV CC /usr/bin/clang
ENV CXX /usr/bin/clang++
ENV LANG=C.UTF-8
ENV TESSDATA_PREFIX=/usr/local/share/tessdata

# Install all build tools needed for our pip installs
RUN apt update 
RUN apt install -y clang g++ make automake autoconf libtool cmake 

## Install the same packages with apt as with apk, but ensure they exist in apt
RUN apt install -y jq git curl
RUN apt install -y file openssl bash tini libpng-dev aspell-en
RUN apt install -y git clang g++ make automake autoconf libtool cmake 
RUN apt install -y autoconf-archive wget 

# Install cuda toolkit
#RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-archive-keyring.gpg
#RUN dpkg -i cuda-archive-keyring.gpg
#RUN rm cuda-archive-keyring.gpg
#RUN apt update
#RUN apt install -y cuda
#RUN echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
#RUN echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
#RUN source ~/.bashrc

# Larger model 
RUN mkdir -p /models

# Fails. 6 bit, 8B model. 
#RUN wget https://huggingface.co/RichardErkhov/meta-llama_-_Meta-Llama-3-8B-gguf/blob/main/Meta-Llama-3-8B.Q6_K.gguf?download=true -O /models/Meta-Llama-3-8B.Q6_K.gguf
#ENV MODEL_PATH="/models/Meta-Llama-3-8B.Q6_K.gguf"

# Simple small Llama wrapper
RUN wget https://huggingface.co/unsloth/DeepSeek-R1-Distill-Llama-8B-GGUF/resolve/main/DeepSeek-R1-Distill-Llama-8B-Q2_K.gguf?download=true -O /models/DeepSeek-R1-Distill-Llama.gguf
# Larger one
#RUN wget https://huggingface.co/unsloth/DeepSeek-R1-Distill-Llama-8B-GGUF/resolve/main/DeepSeek-R1-Distill-Llama-8B-Q8_0.gguf?download=true -O /models/DeepSeek-R1-Distill-Llama.gguf
ENV MODEL_PATH="/models/DeepSeek-R1-Distill-Llama.gguf"

# Failing? Bad magic bytes.
#RUN wget https://huggingface.co/QuantFactory/Llama-3.2-3B-GGUF/resolve/main/Llama-3.2-3B.Q2_K.gguf?download=true -O /models/Llama-3.2-3B.Q2_K.gguf


# Install all of our pip packages in a single directory that we can copy to our base image later
RUN mkdir /install
WORKDIR /install

# Switch back to our base image and copy in all of our built packages and source code
COPY requirements.txt /requirements.txt
RUN python3 -m pip install -r /requirements.txt
RUN CMAKE_ARGS="-DLLAMA_CUBLAS=on" python3 -m pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir


# Install any binary dependencies needed in our final image


# Dev tools
WORKDIR /tmp
#RUN apk update 
#RUN apk upgrade 


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
#RUN wget https://ollama.com/install.sh -O /usr/local/bin/ollama-install
#RUN chmod +x /usr/local/bin/ollama-install
#RUN sh /usr/local/bin/ollama-install
#
#RUN ls -alh /usr/bin
#RUN ollama serve & sleep 2 && ollama pull nezahatkorkmaz/deepseek-v3
#CMD ["sh", "-c", "ollama serve & sleep 2 && python app.py --log-level DEBUG"]

#RUN wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf
RUN python3 -m pip install ctransformers --no-binary ctransformers

# Finally, lets run our app!
ENV GIN_MODE=release
ENV SHUFFLE_APP_SDK_TIMEOUT=300
#ENV LD_LIBRARY_PATH=/usr/local/lib/python3.10/site-packages/ctransformers/lib/basic/libctransformers.so
#RUN chmod 755 /usr/local/lib/python3.10/site-packages/ctransformers/lib/basic/libctransformers.so

COPY src /app
WORKDIR /app
CMD ["python", "app.py", "--log-level", "DEBUG"]
