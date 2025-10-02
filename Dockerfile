# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3-slim

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "backend.src.server.main:app"]

FROM grafana/grafana:8.2.3-ubuntu

EXPOSE 3000
ENV GF_AUTH_DISABLE_LOGIN_FORM "false"

# Allow anonymous authentication or not

ENV GF_AUTH_ANONYMOUS_ENABLED "false"

# Role of anonymous user

ENV GF_AUTH_ANONYMOUS_ORG_ROLE "admin"
 
# Add provisioning
ADD provisioning /etc/Battery_Manufacturing_Digital_Twin/provisioning
# Add configuration file
ADD grafana.ini /etc/Battery_Manufacturing_Digital_Twin/grafana.ini
# Add dashboard json files
ADD dashboards /etc/Battery_Manufacturing_Digital_Twin/dashboards