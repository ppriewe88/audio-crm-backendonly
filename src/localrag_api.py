from fastapi import FastAPI, Form, Request
import uvicorn
import json
import os
import requests
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware # middleware. requirement for frontend-suitable endpoint
debug_imports = False
if not debug_imports:
    import torch
    import openai
else:
    '-----------------------'
    import sys
    print("PYTHON EXE:", sys.executable)
    print("SYS.PATH:", sys.path)
    try:
        import torch
        print("XX TORCH VERSION:", torch.__version__)
    except Exception as e:
        print("EE Fehler beim Import von torch:", e)
        raise
    '-----------------------'
    import sys
    print("PYTHON EXE:", sys.executable)
    print("SYS.PATH:", sys.path)
    try:
        import openai
        from openai import OpenAI
        print("XXXXXX OPENAI VERSION:", openai.__version__)
    except Exception as e:
        print("EEEEEE Fehler beim Import von openai:", e)
        raise
    '-----------------------'


' ############################### setting up app for API #################"'
app = FastAPI()

" ################# middleware block for frontend-suitable endpoint ###############"
# CORS-Middleware. Required for communication with frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://jolly-flower-0edc18203.6.azurestaticapps.net"],  # allow requests from frontend
    allow_credentials=True, 
    allow_methods=["*"],  # allow all HTTP-methods
    allow_headers=["*"],  # allow all headers
)


' ################ initialization block for vault, embeddings, global variables #################'
@app.on_event("startup")
async def startup_event():
    
    # load environment variables to later get openai-key
    load_dotenv(dotenv_path="../.env")

    # configure usage
    global usage 
    usage = "openAI" # "openAI" or "local"

    # if local usage: prepare ollama model for local testing
    if usage == "local":
        pass
    
    # prepare system message and vault content
    llm_active = True
    if llm_active:
        global system_message, vault_content, vault_embeddings, vault_embeddings_tensor, connection, openai_api_key
        openai_api_key =  os.getenv("OPENAI_API_KEY")
        print("OPENAI-KEY:", openai_api_key)

' ###################### endpoint to get storage locations/inventories #################'
@app.post("/say_hello")
async def say_hello(input: str = Form(...)):
    # create query for getting storage locations and inventories
    
    return {"answer": "hello, test successfull!"}

if __name__ == "__main__":
    # my localhost adress
    host = "127.0.0.1"
    uvicorn.run(app, host=host, port=8000)