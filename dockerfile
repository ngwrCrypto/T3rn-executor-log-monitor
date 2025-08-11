FROM python:3.11-slim


RUN pip install --no-cache-dir docker aiohttp


COPY monitor.py /app/monitor.py

WORKDIR /app

CMD ["python", "monitor.py"]