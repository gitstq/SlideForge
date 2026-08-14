# SlideForge
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY slideforge ./slideforge
COPY web ./web
COPY assets ./assets
COPY examples ./examples

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "slideforge.api:app", "--host", "0.0.0.0", "--port", "8000"]
