# Battery Manufacturing Digital Twin API Documentation

This document provides detailed information about the available API endpoints in the Battery Manufacturing Digital Twin system.

## Base URL

```txt
http://localhost:5000
```

## Endpoints

### 1. Home

Returns a welcome message and server status.

- **URL**: `/`
- **Method**: `GET`
- **Response Format**: JSON
- **Response Example**:

```json
{
    "message": "Welcome to the Flask Server!",
    "status": "success"
}
```

### 2. Health Check

Checks the health status of the server.

- **URL**: `/health`
- **Method**: `GET`
- **Response Format**: JSON
- **Response Example**:

```json
{
    "status": "healthy"
}
```

### 3. Start Simulation

Initiates the battery manufacturing simulation process.

- **URL**: `/start_simulation`
- **Method**: `GET`
- **Response Format**: JSON
- **Response Example**:

```json
{
    "status": "simulation started"
}
```

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of requests:

- `200 OK`: The request was successful
- `404 Not Found`: The requested resource was not found
- `500 Internal Server Error`: An error occurred on the server

## Running the Server

The server runs on port 5000 and accepts connections from any IP address (0.0.0.0). To start the server, run:

```bash
python main.py
```

The server will start in debug mode, which is useful for development purposes.
