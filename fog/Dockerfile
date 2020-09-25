FROM ubuntu:18.04

RUN apt-get update -y && \
    apt-get install -y python3-opencv && \
    apt-get install -y python3-pip && \
    apt-get install -y libopencv-dev

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /fog/requirements.txt

WORKDIR /fog

RUN pip3 install --default-timeout=100 -r requirements.txt

COPY . /fog

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]
