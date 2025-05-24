# Audio-based CRM-project (precisely: simulation of a small shop for pet accessories)

# Includes:

    - Speech-controlled Retriever-module (RAG-based) to make smart queries on the database. AI-assisted via openAI-API
    - Speech-controlled Creation-module to execute some standard workflows as making an order, paying an invoice, checking an inventory

# Documentation:

    - More documentation to come!

# Hint: This repo contains the backend only! It serves ONLY for cloud deployment (and local tests)

    - to start it locally, run localrag_api.py. Note: .env will be loaded locally
    - alternatively, start run_app.bat to start this backend. To see how, check heading description in that file.
    - note for docker usage:
       - start docker-container from this project root (easy-local-rag-backendonly), including .env-file:
          - docker run --env-file .env -p 8000:8000 --name bird_paradise_backendcontainer bird_paradise_backend
