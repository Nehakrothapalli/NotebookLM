# Simple Dockerfile using Python 3.12 for local/container deployment
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . ./

# Expose port if needed (Gradio defaults to 7860)
EXPOSE 7860

# Launch the app
CMD ["python", "app.py"]
