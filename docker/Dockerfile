################################# NOTICE ###############################
# This file serves for building a docker container of the BACKEND of crm audio (bird paradise)!
############################### EXECUTION NOTICE #######################
# to build image with this file, ALWAYS start building process from project root! 
# i.e. one level above "docker"-> project root)


################################ backend stage ########################
# import python base image
FROM python:3.12-slim
# create working directory
WORKDIR /app
# install system dependencies for pyodbc and Microsoft ODBC driver
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    gcc \
    g++ \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*
# install Microsoft ODBC Driver 17 for SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*
# copy requirements into root
COPY requirements.txt .
# install requirements with pip
RUN pip install --no-cache-dir -r requirements.txt
# copy contents into root ("." =  /app).
# do this selectively, i.e. manually chose folders!
COPY src/database_access ./src/database_access
COPY src/localrag_api.py ./src/localrag_api.py
COPY src/localrag_functions.py ./src/localrag_functions.py
COPY src/system_helpers.py ./src/system_helpers.py
COPY src/vault.txt ./src/vault.txt

# copy start script from "virtualization" to parent directory of frontend (one level up from docker's WORKDIR!)
COPY docker/run_app_docker.sh /app/run_app_docker.sh

################################ ports and run configuration ##########
# open communication ports
EXPOSE 8000

# command ran during the docker building process
CMD ["bash", "/app/run_app_docker.sh"]