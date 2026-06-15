import novelgen

from prompts.STORY_PROMPTS import INDIA, EPSTEIN, WIFE

print("--- NOVELGEN ONLINE ---")

novel = novelgen.NovelGen()





novel.generate_spine(novel.generate_novel(prompt=WIFE, wordcount=20000, authorial_voice="An imitation of F Scott Fitzgerald mixed with Hemmingway."), regenerate=True)

#novel.generate_novel(prompt=EX, wordcount=20000, authorial_voice="An imitation of F Scott Fitzgerald mixed with Hemmingway.")

#novel.generate_spine("93765826-07c6-4eb3-987e-ab0b3180c49a", regenerate=True)

#novel.generate_characters("af6810a8-c412-4e04-82a8-8a1a779d0dea", regenerate=True)

#novel.generate_chapters("af6810a8-c412-4e04-82a8-8a1a779d0dea", regenerate=True)











