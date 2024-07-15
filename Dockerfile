# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /home/ubuntu/Bitget_API/bitget_proxy_api

# Install pip packages directly
RUN pip install --upgrade pip && \
    pip install python-dotenv aiohttp fastapi pydantic uvicorn docker schedule sqlalchemy psycopg2-binary pandas numpy google-api-python-client google-auth google-auth-oauthlib asyncpg
# Copy the bitget.py script into the container directly
COPY bitget.py .

# Copy the rest of the application code into the container
COPY . .

# Expose the ports that the application uses
EXPOSE 8000 80 5432

# Set the command to run the application
CMD ["uvicorn", "main_api:app", "--host", "0.0.0.0", "--port", "8000"]
