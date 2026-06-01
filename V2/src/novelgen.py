from utils.api_calls import generate_openai, generate_claude
from utils.outline_prompts import GEN_OUTLINE_SYSTEM_PROMPT, GEN_OUTLINE_USER_PROMPT
from utils.generation_prompts import GEN_GENERATION_SYSTEM_PROMPT, GEN_GENERATION_USER_PROMPT

class NovelGen:
    def __init__(self, intro_prompt: str, wordcount: int = 3000):
        print("NovelGen Online")

        # The intro prompt is the north star for the story. It's the user's explicityly directed purpose.
        self.intro_prompt = intro_prompt
        self.wordcount = wordcount


    def generate_outline(self):
        self.outline = generate_openai(
            "gpt-5.4-mini", 
            GEN_OUTLINE_SYSTEM_PROMPT.format(
                intro_prompt=self.intro_prompt, 
                word_count=self.wordcount
            ),
            GEN_OUTLINE_USER_PROMPT
        )
        return self.outline





    def generate_one(self):
        #system_prompt = f"Write a story of approximately {self.wordcount} words."

        '''
        return generate_openai(
            "gpt-5.5", 
            GEN_GENERATION_SYSTEM_PROMPT.format(
                word_count=self.wordcount, 
                outline=self.outline
                ), 
            GEN_GENERATION_USER_PROMPT, 
            )
        '''

        return generate_claude(
            "claude-opus-4-8",
            GEN_GENERATION_SYSTEM_PROMPT.format(
                word_count=self.wordcount,
                outline=self.outline
                ),
            GEN_GENERATION_USER_PROMPT,
        )



