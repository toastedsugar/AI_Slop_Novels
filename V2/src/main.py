import novelgen


# INTRO_PROMPT = "Generate a passionate, seductive, and spicy romance story about a late 30's woman who meets a 19 year old heir to a massive conglomerate, romantically subjugates him, and molds him into the perfect and loyal husband over the course of a year as a girlboss power fantasy. The story is a pyschological thriller about a disfigured abortion doctor that causes women to spit into his mouth with their fingers. The man is a maniacal lunatic who has an insatiable thirst for Red Bull-branded passionfruit spritzers. once he has consumed enough Red Bull-branded passionfruit spritzers, he mutates into a mute-donkey half breed that violently screeches obsenities andcollects caterpillars."

'''
INTRO_PROMPT = "Generate a passionate, seductive, and spicy enemies to lovers story about a broke late 30's to mid 40's single mother who meets a man around 20 years younger than her while on vacation, romantically subjugates him, and molds him into the perfect consenting and loyal husband over the course of a year as a girlboss power fantasy. The nature of their relationship and where, how and why they meet and maintain their relationship is completely up to you. Be as random as you want. The main female lead has massive breasts and a big ass and is a bit chubby. She is clearly a woman who was once beautiful but let herself go. She is warm and sweet on the surface but hides a more dangerous side of herself that she never wants to let anyone see. The main dude is the ultimate ultra handsome bad boy womanizing gigachad mysogynistic but in a female gaze kinda way. He initially oversexualizes her to the point where he comes off as creepy, aggressive, and predetorial because he is used to everyone around him doing whatever he wants them to do. He comes on very strong, touches her innapropriately, makes frequent comments about her breasts, ass, and body and treats her like meat, but she is able to disarm him both physically and mentally and teaches him the real meaning of consent and boundaries, and he is compelled to respect her and not see her as a body to be looked at and fantasized about, but as a strong and independent woman, a woman with intellect and intelligence. The age gap should be a major point of friction between the two where the main dude teases and mocks the main female lead for being old but its just insecurity or something and he ends up succumbing to her awesomeness because she is so sexy in his eyes and she is so competent that he just wants to be with her and make her pleased even though he also has always dreamed of having a submissive housewife that she will never be and he becomes okay with that and becomes a house husband for her instead. He initially fights her authority, but her competence and authority forces him to bow to her will over time. All the lovemaking happens on her terms. She runs the business, she doesn't dress sexy for him no matter how badly he wishes he would do so, she gives orders and he has come to admire her becoming the woman she was always meant to be, just a bit later than she would have liked. She does not take orders from him, sleep with him, or do anything for him sexually unless she wants to. He becomes more and more sexually and emotionally frustrated with her neglect but has learned obedience and empathy and instead uses that frustration to serve and please her more in a non sexual kind of way because that isn't what she wants and he has learned proper consent rather than being a mysogynistic womanizer who treats women like objects rather than people with feelings and emotions. Even until the end, he resists her authority, but they both know it's just an act and he will inevitably succumb."
'''

'''
INTRO_PROMPT = "Generate a passionate, seductive, and spicy male power fantasy about a pathetic loser middle aged male who is broke, unemployed, fat, and balding (norwood 7) who attracts a diverse group of beautiful women, all of whom completely submit to him without question and compete to see which of them can service him the best. Main dude think's he's struck it big, but forgot that he lives in Flint, Michigan, and the high lead concentration in the water supply and the unimaginable amount of asbestos in the walls have driven everyone mad and now act uncharacteristically. The girls, and maybe him as well. As the world goes crazy, he begins to have visions of other dimensions where he lives infitite scenarios from the mundane to the fantastical all at the same time, and maybe not at all. As he begins to ascend to a higher plane of existence, the rest of his body begins to bald, and the girls around him merge into a singularity that loves him at his finest."
'''

'''
INTRO_PROMPT = "I just want a love story but like the kind of love story that isnt about love, its subtext for mental health and its kind of a dystopian story about a world where there is no love, just hate and hate for hate and hate for hate for hate but then love comes in and destroys everything while the main character is the only one left alive but its a love story about how love destroys everything."
'''

'''
INTRO_PROMPT = "Surprise me."
'''

'''
INTRO_PROMPT = "Write me a story about Epstein's boat. A cruise ship where wealthy people do crazy hedonistic things outside the rule of law. But when Mossad, the CIA, FBI, KGB, and all the other intelligence organizations arrive on the ship, the protagonist realizes that the ship is populated entirely by spies from nations and there are no real criminals on board, its just the organizations themselves being hedonistic and disgusting and whatever on the taxpayers dime treating the boat like a party boat."
'''

'''
INTRO_PROMPT = "An American tourist visits Korea but somehow ends up in the wrong one. She is brutally tortured and subjugated and made to consume propoganda until she learns the true power of the People's Republic and communism and returns to America a changed woman who wholeheartedly believes in the power of collectivism and communism. Long live the People's republic of Korea!"
'''

INTRO_PROMPT = "Romantasy. Squirrel. Nut. Yes."
novel = novelgen.NovelGen(INTRO_PROMPT)

slop_outline = novel.generate_outline()
print(slop_outline)

print("\n\n\n\n\n")

slop = novel.generate_one()
print(slop)

