import ollama
import os
import yaml

from utils.prompt_render import render_character_prompt, render_system_prompt, render_location_prompt, render_chapter_prompt, render_object_prompt

from src.blueprint import Blueprint

class NovelGen:
    def __init__(self, blueprint:Blueprint):
        self.blueprint = blueprint
        print("NovelGen Online")


        # Put together the system prompt here
        system_prompt = render_system_prompt(self.blueprint.data)
        print(system_prompt)

        user_prompt = self.build_user_prompt(1)
        print (user_prompt)
        
        


        # call ollama or whatever to generate the text
        # self.generate("ollama", system_prompt + "\n\n\n" + user_prompt)





    def build_user_prompt(self, chapter_number):
        # Pull information for this chapter from the blueprint
        chapter = self.blueprint.get_chapter(chapter_number)
        #print(chapter)

        character_list = chapter.get('characters_present', [])
        location_list = chapter.get('locations_present', [])
        object_list = chapter.get('objects_present', [])

        character_prompt = ""
        location_prompt = ""
        object_prompt = ""
        
        # Loop through all the characters in this chapter and build a prompt for each
        for character_id in character_list:
            try:
                character_prompt += render_character_prompt(self.blueprint.get_character(character_id))
            except Exception as e:
                print(e)
        #print(character_prompt)

        # Loop through all the locations in this chapter and build a prompt for each
        for location_id in location_list:
            try:
                location_prompt += render_location_prompt(self.blueprint.get_location(location_id))
            except Exception as e:
                print(e)
        #print(location_prompt)

        # Loop through all the objects in this chapter and build a prompt for each
        for object_id in object_list:
            try:
                object_prompt += render_object_prompt(self.blueprint.get_object(object_id))
            except Exception as e:
                print(e)
        #print(object_prompt)    


        # Build a finished prompt for this chapter specific information
        try:
            chapter = render_chapter_prompt(chapter)
        except Exception as e:
            print(e)
        #print(chapter)

        return f"{character_prompt}{location_prompt}{object_prompt}{chapter}"



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

    