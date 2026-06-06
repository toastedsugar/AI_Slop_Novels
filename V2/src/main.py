import novelgen
import json

from prompts.STORY_PROMPTS import SQUIRREL

print("--- NOVELGEN ONLINE ---")

'''

# Simple slop pipeline
novel = novelgen.NovelGen(INTRO_PROMPT, wordcount=2000)

slop_outline = novel.generate_outline_simple()
print(slop_outline)

print("\n\n\n\n\n")

#slop = novel.generate_oneshot()
slop = novel.generate_story()

print(slop)

'''





# Advanced slop pipeline
novel = novelgen.NovelGen(SQUIRREL, wordcount=5000)

slop_outline = novel.generate_outline()
print(json.dumps(json.loads(slop_outline), indent=2))

print("\n\n\n\n\n")

#slop = novel.generate_oneshot()
#slop = novel.generate_story()

#print(slop)


'''
'''