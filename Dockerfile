# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install the required packages using pip
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire current directory to the working directory in the container
COPY . .

# Expose the port that your Streamlit app listens on (usually 8501)
EXPOSE 8501

# Set the command to run your Streamlit app when the container starts
CMD ["streamlit", "run", "app.py"]