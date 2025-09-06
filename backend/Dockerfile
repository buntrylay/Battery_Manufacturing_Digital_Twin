# 1. Start with an official Python base image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Define PYTHONPATH explicitly
ENV PYTHONPATH=/app/src

# 4. Copy just the requirements file first, to leverage Docker's caching
COPY requirements.txt .

# 5. Install your Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your application's source code
COPY ./src ./src

# 7. Expose the port your app runs on
EXPOSE 8000

# 7. Define the command to run your FastAPI application
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]