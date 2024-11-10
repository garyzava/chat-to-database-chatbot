# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy files
#COPY app.py /app/
COPY chat2dbchatbot /app/
#COPY db/database_setup.sql /db/
COPY db /db/

# Install dependencies
#RUN pip install streamlit psycopg2-binary

#Copy requirements.txt and .env to the image
COPY requirements.txt /app/
COPY .env /app/

# Install dependencies
RUN pip install -r requirements.txt

# Expose the Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]