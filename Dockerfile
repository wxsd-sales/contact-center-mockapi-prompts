############################################################
# Dockerfile to build CCPrompts App
############################################################
#sudo docker build -t ccprompts .
#sudo docker run -p 10031:10031 -i -t ccprompts
#Change 10031 in both places on the above line to be the value of MY_APP_PORT in your .env file
###########################################################################

FROM python:3.8.1

# File Author / Maintainer
MAINTAINER "Taylor Hanson <tahanson@cisco.com>"

# Copy the application folder inside the container
ADD . .

# Set the default directory where CMD will execute
WORKDIR /

# Get pip to download and install requirements:
RUN pip install python-dotenv
RUN pip install tornado==4.5.2

# Set the default command to execute
# when creating a new container
CMD ["python","-u","server.py"]
