FROM python:3.8

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p graphs
RUN mkdir -p data

ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "python ./src/launcher.py $BOT_CLASS"]