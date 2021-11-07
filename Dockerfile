# syntax=docker/dockerfile:1

FROM python:3
# Unbuffered python output for friendliness with Docker logging
ENV PYTHONUNBUFFERED=1

# Install necessary system packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-server

# Copy files and install python packages
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

#SSH
ENV SSH_PASSWD "root:Docker!"
RUN echo "$SSH_PASSWD" | chpasswd
COPY sshd_config /etc/ssh/

# Set up init script and expose ports
COPY init.sh /usr/local/bin/
RUN chmod u+x /usr/local/bin/init.sh
EXPOSE 8000 2222
ENTRYPOINT ["init.sh"]