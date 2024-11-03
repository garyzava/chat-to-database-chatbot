# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy files
COPY app.py /app/
COPY db/database_setup.sql /db/

# Install dependencies
#RUN pip install streamlit psycopg2-binary

#Copy requirements.txt to the image
COPY requirements.txt /app/  

# Install dependencies
RUN pip install -r requirements.txt


# Expose the Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]