FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy the requirement files and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Command to run the script
CMD ["python", "main.py"]