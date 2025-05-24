import ollama
import os
import argparse
from system_helpers import find_sql_query, CYAN, YELLOW, NEON_GREEN, RESET_COLOR
from database_access.data_retrieval import establish_database_connection, make_query
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
        print("XXXXXX TORCH VERSION:", torch.__version__)
    except Exception as e:
        print("EEEEEE Fehler beim Import von torch:", e)
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

' ######################################## systems preparation functions #######################'
def parse_cli_input():
    # Parse command-line arguments
    print(NEON_GREEN + "Parsing command-line arguments..." + RESET_COLOR)
    parser = argparse.ArgumentParser(description="Ollama Chat")
    parser.add_argument("--model", default="llama3", help="Ollama model to use (default: llama3)")
    args = parser.parse_args()
    return args

def configure_ollama_client():
    # Configuration for the Ollama API client
    print(NEON_GREEN + "Initializing Ollama API client..." + RESET_COLOR)
    client = OpenAI(
        base_url='http://localhost:11434/v1',
        api_key='llama3'
    )
    return client

def load_vault_content():
    # Load the vault content
    print(NEON_GREEN + "Loading vault content..." + RESET_COLOR)
    vault_content = []
    if os.path.exists("vault.txt"):
        with open("vault.txt", "r", encoding='utf-8') as vault_file:
            vault_content = vault_file.readlines()
    return vault_content

def generate_embeddings_for_vault_content(vault_content):
    # Generate embeddings for the vault content using Ollama
    print(NEON_GREEN + "Generating embeddings for the vault content..." + RESET_COLOR)
    vault_embeddings = []
    for content in vault_content:
        response = ollama.embeddings(model='mxbai-embed-large', prompt=content)
        vault_embeddings.append(response["embedding"])
    return vault_embeddings

def generate_vault_embeddings_tensor(vault_embeddings):
    # Convert to tensor and print embeddings
    print(NEON_GREEN + "Converting embeddings to tensor..." + RESET_COLOR)
    vault_embeddings_tensor = torch.tensor(vault_embeddings) 
    # print("Embeddings for each line in the vault:")
    # print(vault_embeddings_tensor)
    return vault_embeddings_tensor

' ##################################################### ollama functions #######################'
# Function to get relevant context from the vault based on user input
def get_relevant_context(user_input, vault_embeddings, vault_content, top_k=3):
    if vault_embeddings.nelement() == 0:  # Check if the tensor has any elements
        return []
    # Encode the rewritten input
    input_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=user_input)["embedding"]
    # Compute cosine similarity between the input and vault embeddings
    cos_scores = torch.cosine_similarity(torch.tensor(input_embedding).unsqueeze(0), vault_embeddings)
    # Adjust top_k if it's greater than the number of available scores
    top_k = min(top_k, len(cos_scores))
    # Sort the scores and get the top-k indices
    top_indices = torch.topk(cos_scores, k=top_k)[1].tolist()
    # Get the corresponding context from the vault
    relevant_context = [vault_content[idx].strip() for idx in top_indices]
    # print found tables
    if relevant_context:
        relevant_tables = tables_in_relevant_context(relevant_context)
    else:
        print(CYAN + "No relevant context found." + RESET_COLOR)
    
    return {"relevant_context":relevant_context, "relevant_tables":relevant_tables}

def tables_in_relevant_context(relevant_context):
    # Extract table names from the relevant context
    table_names = []
    print("\nPulled context (tables):")
    for line in relevant_context:
        start = len("CREATE TABLE [dbo].") + 1
        end = line.find("]", start)
        table_name = line[start:end]
        table_names.append(table_name)
        print("table name:", CYAN + table_name + RESET_COLOR)
    return table_names

# Function to call chat with retrieved context of user query
def ollama_chat_no_memory(client, user_input, system_message, vault_embeddings_tensor, vault_content, ollama_model):
    # Get relevant context from the vault
    relevant_context = get_relevant_context(user_input, vault_embeddings_tensor, vault_content, top_k=2)["relevant_context"]
    if relevant_context:
        # Convert list to a single string with newlines between items
        context_str = "\n".join(relevant_context)
        # alternatively: take all lines of context (each corresponds to a table!!) and extract table names for print
        print("\nPulled context (tables):")
        for line in relevant_context:
            start = len("CREATE TABLE [dbo].") + 1
            end = line.find("]", start)
            table_name = line[start:end]
            print("table name:", CYAN + table_name + RESET_COLOR)
    else:
        print(CYAN + "No relevant context found." + RESET_COLOR)
    
    # Prepare the user's input by concatenating it with the relevant context
    user_input_with_context = user_input
    if relevant_context:
        user_input_with_context = context_str + "\n\n" + user_input
        
    # Create a message history including the system message and the conversation history
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_input_with_context}
    ]

    print("\nmessage ready\nentering chat....")
    response = client.chat.completions.create(
        model=ollama_model,
        messages=messages,
        max_tokens=100,
        temperature=0.1,
        stream=True
    )
    print("message retrieved:\n")
    full_response = ""
    for chunk in response:
        content_part = chunk.choices[0].delta.content or ""
        print(NEON_GREEN + content_part + RESET_COLOR, end="", flush=True)
        full_response += content_part
    print("")
    
    return full_response

' ############################################################# starting main program ##########'

if __name__ == "__main__":
    # prepare system
    args = parse_cli_input()
    client = configure_ollama_client()
    system_message =  find_sql_query
    vault_content = load_vault_content()
    vault_embeddings = generate_embeddings_for_vault_content(vault_content)
    vault_embeddings_tensor = generate_vault_embeddings_tensor(vault_embeddings)
    connection = establish_database_connection()

    # Conversation loop
    print("Starting querying loop...")

    while True:
        user_input = input("\n" + YELLOW + "Ask a query about your documents (or type 'quit' to exit): " + RESET_COLOR)
        if user_input.lower() == 'quit':
            connection.close()
            print("CONNECTION CLOSED!")
            break
        
        # get response from LLM
        response = ollama_chat_no_memory(
                            client = client,
                            user_input = user_input, 
                            system_message=system_message, 
                            vault_embeddings_tensor=vault_embeddings_tensor, 
                            vault_content=vault_content, 
                            ollama_model = args.model)
        
        # extract sql query and send to database
        response_query = response[len("[Query:]"):]
        result = make_query(response_query, connection)
        print(result)

