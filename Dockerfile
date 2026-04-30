# Use Python base image
FROM python:3.10

# Set working directory
WORKDIR /app

#Install dependencies
COPY requirements.txt .

RUN pip install -r requirements.txt

# Copy files
COPY . .


# Run app
CMD ["python", "app.py"]
