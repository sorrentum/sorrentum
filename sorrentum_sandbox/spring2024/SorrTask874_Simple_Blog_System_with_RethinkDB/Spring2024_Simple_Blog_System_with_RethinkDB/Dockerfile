FROM python:3.8.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

ENV NAME World

CMD ["python", "app.py"]
