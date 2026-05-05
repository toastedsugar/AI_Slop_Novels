import ollama
import os
import yaml

from utils.prompt_render import render_character_prompt, render_system_prompt, render_location_prompt

from src.blueprint import Blueprint

class NovelGen:
    def __init__(self, blueprint:Blueprint):
        self.blueprint = blueprint
        print("NovelGen Online")


        # Printing metadatinformationa to confirm blueprint is readable
        # print(blueprint.get_metadata())






        # put together the system prompt here
        system = render_system_prompt(self.blueprint.data)
        print(system)

        

        

        
        # Put together user prompt here
        try:
            character = render_character_prompt(self.blueprint.get_character("thistle"))
        except Exception as e:
            print(e)   
        print(character)    

        try:
            location = render_location_prompt(self.blueprint.get_location("greenwood"))
        except Exception as e:
            print(e)    
        #print(location)





        # call code to generate chapter








        # call ollama or whatever to generate the model
        #self.generate("ollama", self.Generate_Chapter())


    def generate(self, model, prompt):
        """
        Connects to Ollama and generates a response for the given prompt.

        Args:
            model: Ignored — actual model is read from OLLAMA_MODEL env var (default: llama3).
            prompt: The prompt string to send to the model.

        Prints the prompt and the model's response. Raises on non-model errors.
        """

        host = os.getenv("OLLAMA_HOST") or "http://localhost:11434"
        client = ollama.Client(host=host)
        model = os.getenv("OLLAMA_MODEL", "llama3")
        print(prompt)

        try:
            response = client.generate(model=model, prompt=prompt, stream=False)
            print(response['response'])
        except Exception as e:
            if "model" in str(e).lower() and "not found" in str(e).lower():
                print(f"Error: Model '{model}' is not downloaded.")
                print(f"Run: docker exec ollama ollama pull {model}")
            else:
                raise










    def get_ids_from_yaml(blueprint_data: list) -> list[str]:
        return [item["id"] for item in blueprint_data]

    def load_yaml(self, yaml_path: str) -> dict:
        with open(yaml_path) as f:
            return yaml.safe_load(f)

    