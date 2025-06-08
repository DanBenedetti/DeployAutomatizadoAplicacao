FROM python:3.11

WORKDIR /app

RUN apt-get update \
    && apt-get install -y build-essential default-libmysqlclient-dev

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

EXPOSE 8086

CMD ["flask", "run", "--host=0.0.0.0", "--port=8086"]
