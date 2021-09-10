FROM python:3.8-alpine

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt

COPY deploy.py /deploy.py

CMD [ "python", "/deploy.py" ]