################################# NOTICE ##########################
# This script starts the uvicorn server in the docker container!
################################# NOTICE ##########################
# navigate to src directory
cd /app/src
# start uvicorn server (api) in docker (& tell it to run in the background)
uvicorn api_server:app --host 0.0.0.0 --port 8000