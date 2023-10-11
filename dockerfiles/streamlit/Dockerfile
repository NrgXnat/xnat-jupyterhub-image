#FROM codercom/code-server:latest
#
## Install dependencies
#RUN sudo apt-get update && \
#    sudo apt-get install -y \
#        build-essential \
#        curl \
#        git \
#        libssl-dev \
#        libffi-dev \
#        python3-dev \
#        python3-pip \
#        python3-venv \
#        wget
#
#RUN pip install jhsingle-native-proxy jupyterhub streamlit
FROM python:3.7
RUN pip3 install \
    jupyterhub \
    jhsingle-native-proxy \
    streamlit

# create a user, since we don't want to run as root
RUN useradd -m jovyan
ENV HOME=/home/jovyan
WORKDIR $HOME
USER jovyan

EXPOSE 8888

WORKDIR /app

COPY intro.py /app/intro.py

CMD ["jhsingle-native-proxy", "--destport", "8505", "streamlit", "run", "/app/intro.py", "{--}server.port", "{port}", "{--}server.headless", "True", "{--}server.enableCORS", "False"]