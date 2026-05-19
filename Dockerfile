FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir flask gunicorn

COPY app_web_clean.py .

EXPOSE 5000

ENV PORT=5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app_web_clean:app"]
