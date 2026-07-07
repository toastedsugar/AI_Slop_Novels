import novelgen

from prompts.STORY_PROMPTS import OFFICE, AIRCON

print("--- NOVELGEN ONLINE ---")

novel = novelgen.NovelGen()

#slop = novel.generate()




# Pulling a story and spine
novel.gen_spine(novel.gen_novel(prompt=AIRCON, wordcount=70000, authorial_voice="An imitation of F Scott Fitzgerald mixed with Hemmingway."), regen=True)


#novel.gen_novel(MOMMY, 50000, authorial_voice="An imitation of F Scott Fitzgerald mixed with Hemmingway.")

def gen_story(id: str):
    #novel.gen_spine(id, regen=True)

    #novel.gen_characters(id, regen=True)
    #novel.gen_locations(id, regen=True)
    #novel.gen_items(id, regen=True)
    #novel.gen_organizations(id, regen=True)
    #novel.gen_events(id, regen=True)

    #novel.gen_chapter_list(id, regen=True)
    
    #novel.gen_chapter_outline(id, regen=True)
    #novel.gen_chapter_from_outline(id, 12)
    
    novel.gen_chapter_raw(id, 23)



#gen_story("d5cf6780-b7d1-4274-92fd-afe66f3881e8")





