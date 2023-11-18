REM Build Docker Image
docker build -t dwellist -f docker/Dockerfile .

REM Run Docker Container
docker run -d -p 5000:5000 dwellist