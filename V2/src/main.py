import novelgen

from prompts.STORY_PROMPTS import INDIA, EPSTEIN, WIFE, KARMA, SPACE_AMERICA

print("--- NOVELGEN ONLINE ---")

novel = novelgen.NovelGen()




# Pulling a story and spine
#novel.generate_spine(novel.generate_novel(prompt=SPACE_AMERICA, wordcount=25000, authorial_voice="An imitation of F Scott Fitzgerald mixed with Hemmingway."), regenerate=True)


#novel.generate_novel(SPACE_AMERICA, 25000, authorial_voice="An imitation of F Scott Fitzgerald mixed with Hemmingway.")

#novel.generate_spine("5ab83283-eb82-42ac-ae4c-8537e98aad62", regenerate=True)

#novel.generate_characters("5ab83283-eb82-42ac-ae4c-8537e98aad62", regenerate=True)

#novel.generate_chapter_list("5ab83283-eb82-42ac-ae4c-8537e98aad62", regenerate=True)

novel.generate_chapters("5ab83283-eb82-42ac-ae4c-8537e98aad62", regenerate=True)










