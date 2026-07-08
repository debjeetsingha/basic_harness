from langfuse import get_client
from pydantic_ai import Agent

langfuse = get_client()

def start_tracing():
    langfuse = get_client()
    if langfuse.auth_check():
        print("Langfuse client is authenticated and ready!")
    else:
        print("Authentication failed. Please check your credentials and host.")
        
    Agent.instrument_all()
