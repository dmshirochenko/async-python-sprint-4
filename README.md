# URL Shortener Service

This project is a URL shortening service that allows users to create shorter aliases for long URLs. It also provides detailed analytics on the usage of these shortened URLs. The service is designed with an emphasis on simplicity, performance, and reliability.

## Features

- **URL Shortening:** Convert long URLs into manageable short links.
- **User Management:** Allow users to create public or private links and manage their visibility.
- **Database Interaction:** Custom database interactions with transaction support.

## Getting Started

### Prerequisites

- Python 3.8+
- FastAPI
- PostgreSQL (Version 10+)
- Uvicorn (for running the FastAPI app)


### Server Installation

1. **Clone the Repository**
   ```
   git clone git@github.com:dmshirochenko/async-python-sprint-4.git
   ```
2. **.ENV file creation**
    ```
    Create .env file using .env.example
    ```
2. **To Start the Server**
    ```
    make start
    ```
3. **To Stop the Server**
    ```
    make stop
    ```
4. **Open API documentation**
    ```
    For a server running on localhost, access it via:
    http://127.0.0.1:8000/docs
    ```

# Endpoint Documentation

Available at the /docs path. 
For a server running on localhost, access it via:
http://127.0.0.1:8000/docs

