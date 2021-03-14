FROM python:3.8

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p graphs
RUN mkdir -p data

CMD ["python", "./src/test.py"]