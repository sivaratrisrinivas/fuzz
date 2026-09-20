FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    FUZZ_CORS_ORIGINS=http://localhost:3000 \
    FUZZ_RATE_LIMIT_PER_MINUTE=30 \
    FUZZ_SMART_ROBOT_TIMEOUT_S=45

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src /app/src
COPY prompts /app/prompts

EXPOSE 8000

CMD ["uvicorn", "thin_helper.main:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "75"]
