# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.11-slim

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app

# Set PYTHONPATH to include the backend source directory
ENV PYTHONPATH=/app/backend/src

COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["uvicorn", "src.server.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM grafana/grafana:8.2.3-ubuntu

EXPOSE 3000

# Grafana configuration will be handled via grafana.ini and environment variables
# Remove hardcoded auth settings for security
 
# Add provisioning
ADD provisioning /etc/Battery_Manufacturing_Digital_Twin/provisioning
# Add configuration file
ADD grafana.ini /etc/Battery_Manufacturing_Digital_Twin/grafana.ini
# Add dashboard json files
ADD dashboards /etc/Battery_Manufacturing_Digital_Twin/dashboards