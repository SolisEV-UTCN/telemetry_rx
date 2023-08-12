FROM python:3.11-bookworm

WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get install -y libusb-1.0.0

COPY --chmod=644 src_rx/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --chmod=755 src_rx/ ./

CMD python main.py
