import ollama
import os

from src.blueprint import Blueprint

class NovelGen:
    def __init__(self, blueprint:Blueprint):
        self.blueprint = blueprint
        print("NovelGen Online")

    

    def run(self, URL):
        # Connect to Ollama using environment variable, use hardcoded value if not found
        host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
        client = ollama.Client(host=host)

        # Generate text llama-13b
        response = client.generate(
            model=os.getenv("OLLAMA_MODEL", "llama3")
            prompt='Write a short character description for a dark prince.',
            stream=False
        )

        print(response['response'])
        print("Running")





def Generate_Chapter(self):
        print("Generating")

