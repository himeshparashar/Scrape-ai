# Use an official Python runtime as a parent image
FROM python:3.11
 
# Set the working directory to /app
WORKDIR /application
COPY requirements.txt .

RUN pip install --upgrade pip

ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
# RUN apt update && apt install chromium -y  
# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt


# Adding trusting keys to apt for repositories
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Adding Google Chrome to the repositories
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Updating apt to see and install Google Chrome
RUN apt-get -y update

# Magic happens
RUN apt-get install -y google-chrome-stable

# Copy the current directory contents into the container at /app
COPY . /application

RUN chmod +x chromedriver/chromedriver 
# Expose port 8000 for FastAPI to run on
EXPOSE 8000
 
# Command to run your application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
