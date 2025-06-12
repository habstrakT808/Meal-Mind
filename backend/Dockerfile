FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install requests

COPY . .

ENV FLASK_APP=run.py
ENV FLASK_ENV=development
ENV FLASK_DEBUG=0

EXPOSE 5000

CMD ["python", "run.py"] 