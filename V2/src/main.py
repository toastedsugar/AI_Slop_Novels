import novelgen

from prompts.STORY_PROMPTS import INDIA

print("--- NOVELGEN ONLINE ---")

novel = novelgen.NovelGen()



# print(novel.generate_novel(prompt=INDIA, wordcount=20000, authorial_voice="male"))

# novel.generate_spine("be5777a6-ee62-47c9-8221-7cfd9322f1de", regenerate=True)

#novel.generate_characters("be5777a6-ee62-47c9-8221-7cfd9322f1de", regenerate=True)

novel.generate_chapters("be5777a6-ee62-47c9-8221-7cfd9322f1de", regenerate=True)
