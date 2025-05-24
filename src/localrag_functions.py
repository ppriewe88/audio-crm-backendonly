import os
import argparse
from system_helpers import find_sql_query, CYAN, YELLOW, NEON_GREEN, RESET_COLOR
from database_access.data_retrieval import establish_database_connection, make_query
import torch
from openai import OpenAI

' ######################################## systems preparation functions #######################'

def load_vault_content():
    # Load the vault content
    print(NEON_GREEN + "Loading vault content..." + RESET_COLOR)
    vault_content = []
    if os.path.exists("vault.txt"):
        with open("vault.txt", "r", encoding='utf-8') as vault_file:
            vault_content = vault_file.readlines()
    return vault_content

def configure_openai_client():
    
    print(NEON_GREEN + "Initializing OPENAI client..." + RESET_COLOR)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable not found!")
    
    client = OpenAI(api_key=openai_api_key)
    return client

def generate_embeddings_for_vault_content(vault_content, openai_client):
    
    print(NEON_GREEN + "Generating embeddings for the vault content..." + RESET_COLOR)    
    vault_embeddings = []
    client = openai_client
    
    for content in vault_content:
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",  # oder "text-embedding-3-large" für bessere Qualität
                input=content.strip()
            )
            vault_embeddings.append(response.data[0].embedding)
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Fallback: leeres Embedding oder überspringen
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
def get_relevant_context(user_input, openai_client, vault_embeddings, vault_content, top_k=3):
    if vault_embeddings.nelement() == 0:  # Check if the tensor has any elements
        return []
    client = openai_client
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=user_input
        )
        input_embedding = response.data[0].embedding
    except Exception as e:
        print(f"Error generating user input embedding: {e}")
        return {"relevant_context": [], "relevant_tables": []}
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