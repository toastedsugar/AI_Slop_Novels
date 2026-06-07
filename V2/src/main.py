import novelgen
import json

from prompts.STORY_PROMPTS import INDIA, PRISON_BUS

print("--- NOVELGEN ONLINE ---")


# Sop pipeline
novel = novelgen.NovelGen(PRISON_BUS, wordcount=5000)

slop_outline = novel.generate_outline()
print(json.dumps(json.loads(slop_outline), indent=2))

print("\n\n\n\n\n")

#slop = novel.generate_story()

#print(slop)


'''
'''