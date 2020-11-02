FROM ubuntu:18.04

COPY philips-pathologysdk-2.0-ubuntu18_04_py36_research.zip /tmp/philips-pathologysdk-2.0-ubuntu18_04_py36_research.zip

RUN apt update && apt install -y python3 python3-pip python3-numpy python3-openslide unzip gdebi

RUN unzip /tmp/philips-pathologysdk-2.0-ubuntu18_04_py36_research.zip -d /tmp && \
    gdebi -n /tmp/philips-pathologysdk-2.0-ubuntu18_04_py36_research/pathologysdk-modules/*pixelengine*.deb && \
    gdebi -n /tmp/philips-pathologysdk-2.0-ubuntu18_04_py36_research/pathologysdk-python36-modules/*python3-pixelengine*.deb && \
    gdebi -n /tmp/philips-pathologysdk-2.0-ubuntu18_04_py36_research/pathologysdk-modules/*eglrendercontext*.deb && \
    gdebi -n /tmp/philips-pathologysdk-2.0-ubuntu18_04_py36_research/pathologysdk-python36-modules/*python3-eglrendercontext*.deb && \
    gdebi -n /tmp/philips-pathologysdk-2.0-ubuntu18_04_py36_research/pathologysdk-modules/*gles2renderbackend*.deb && \
    gdebi -n /tmp/philips-pathologysdk-2.0-ubuntu18_04_py36_research/pathologysdk-python36-modules/*python3-gles2renderbackend*.deb && \
    gdebi -n /tmp/philips-pathologysdk-2.0-ubuntu18_04_py36_research/pathologysdk-modules/*gles3renderbackend*.deb && \
    gdebi -n /tmp/philips-pathologysdk-2.0-ubuntu18_04_py36_research/pathologysdk-python36-modules/*python3-gles3renderbackend*.deb && \
    gdebi -n /tmp/philips-pathologysdk-2.0-ubuntu18_04_py36_research/pathologysdk-modules/*softwarerenderer*.deb && \
    gdebi -n /tmp/philips-pathologysdk-2.0-ubuntu18_04_py36_research/pathologysdk-python36-modules/*python3-softwarerenderbackend*.deb && \
    gdebi -n /tmp/philips-pathologysdk-2.0-ubuntu18_04_py36_research/pathologysdk-python36-modules/*python3-softwarerendercontext*.deb && \
    rm -rf /tmp/philips-pathologysdk-2.0-ubuntu18_04_py36_research && rm /tmp/philips-pathologysdk-2.0-ubuntu18_04_py36_research.zip

RUN pip3 install gunicorn flask

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./app /app
WORKDIR /app/

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]