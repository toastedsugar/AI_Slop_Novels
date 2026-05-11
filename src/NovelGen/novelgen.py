import yaml

from utils.prompt_render import render_character_prompt, render_system_prompt, render_location_prompt, render_chapter_prompt, render_object_prompt
from utils.api_calls import generate_openai, generate_ollama, generate_claude, generate_gemini

from src.blueprint import Blueprint

class NovelGen:
    def __init__(self, blueprint:Blueprint):
        self.blueprint = blueprint
        print("NovelGen Online")


        # Put together the system prompt here
        system_prompt = render_system_prompt(self.blueprint.data)
        #print(system_prompt)

        user_prompt = self.build_user_prompt(1)
        #print (user_prompt)
        
    

        '''
        ollama_output = self.generate_ollama(
            "ollama", 
            system_prompt + "\n\n\n" + user_prompt
        )
        print(ollama_output)
        '''
        '''
        openai_output = generate_openai(
            "gpt-5-mini",
            system_prompt,
            user_prompt
        )
        print(openai_output)
        '''

        claude_output = generate_claude(
            "claude-sonnet-4-6",
            system_prompt,
            user_prompt
        )
        print(claude_output)
        '''
        gemini_output = generate_gemini(
            "gemini-2.5-flash",
            system_prompt,
            user_prompt
        )
        print(gemini_output)
        '''



        print("\n\n\nD O N E")



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


    