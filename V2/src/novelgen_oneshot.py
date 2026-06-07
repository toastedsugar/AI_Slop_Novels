import os
from utils.model_routing import load_routing, generate_from_config
from prompts.outline_simple import GEN_SIMPLE_OUTLINE_SYSTEM_PROMPT, GEN_SIMPLE_OUTLINE_USER_PROMPT
from prompts.generation_oneshot import GEN_ONESHOT_SYSTEM_PROMPT, GEN_ONESHOT_USER_PROMPT


class NovelGenOneshot:
    def __init__(self, intro_prompt: str, wordcount: int = 3000, authorial_voice: str = ""):
        print("NovelGenOneshot Online")
        self.routing = load_routing()
        print(f"Routing env: {os.environ.get('ENV', 'test')}")

        self.intro_prompt = intro_prompt
        self.wordcount = wordcount
        self.authorial_voice = authorial_voice

    def generate_outline_simple(self):
        config = self.routing["final_outline"]
        print(f"Generating outline using {config['provider']} / {config['model']}")
        self.outline = generate_from_config(
            config,
            GEN_SIMPLE_OUTLINE_SYSTEM_PROMPT.format(
                intro_prompt=self.intro_prompt,
                word_count=self.wordcount
            ),
            GEN_SIMPLE_OUTLINE_USER_PROMPT
        )
        return self.outline

    def generate_oneshot(self):
        config = self.routing["prose"]
        print(f"Generating prose using {config['provider']} / {config['model']}")
        return generate_from_config(
            config,
            GEN_ONESHOT_SYSTEM_PROMPT.format(
                word_count=self.wordcount,
                outline=self.outline
            ),
            GEN_ONESHOT_USER_PROMPT,
        )
