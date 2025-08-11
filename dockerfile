FROM python:3.11-slim

# for logging without buffering
ENV PYTHONUNBUFFERED=1

# install requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy code
COPY monitor.py /app/monitor.py

WORKDIR /app

CMD ["python3", "-u", "monitor.py"]