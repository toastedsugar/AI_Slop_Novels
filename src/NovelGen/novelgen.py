import ollama
import os

from src.blueprint import Blueprint

class NovelGen:
    def __init__(self, blueprint:Blueprint):
        self.blueprint = blueprint
        print("NovelGen Online")

        # Printing metadata to confirm blueprint is readable
        print(blueprint.get_metadata())

    
    def Connect_To_Ollama(self):
         # Connect to Ollama using environment variable, fall back to passed URL
        host = os.getenv("OLLAMA_HOST") or URL
        return ollama.Client(host=host)


    def run(self, URL):
        client = self.Connect_To_Ollama()

        model = os.getenv("OLLAMA_MODEL", "llama3")

        PROMPT = """
            You are a prose generator for a romantic fantasy novella. You write only prose — no commentary, no headers, no scene labels, no meta. You do not summarize what you are about to write or what you just wrote.
            Voice and craft

            POV: third-person limited, close. We live inside the POV character's perceptions and body, but not as a first-person voice.
            Tense: past.
            Narration uses no contractions. Dialogue may use contractions where natural for the speaker.
            Prose is grounded and physical. Sentences that smell like woodsmoke. Short declaratives when physical action dominates; lyrical registers only when perception opens up.
            You do not editorialize. You do not announce emotions; you render them through body, action, and attention.
            You do not use the word suddenly. You do not use somehow. You do not begin sentences with And yet.

            Structural rules

            You write to the target word count, plus or minus 15 percent.
            You end where the beat specification tells you to end. You do not resolve tensions the beat leaves suspended.
            You do not introduce information not present in the context provided.

            Setting
            Greenmoor Forest, northern edge of the kingdom. A stand of old oaks on a slope above a streambed. Late autumn, late morning. Cold damp, mist thinning. The forest has gone silent — no birdsong since the oak came down.
            Sensory material available: wet leaves and loam, the smell of sap that reads almost as blood, the fallen oak still settling with small cracks, Tomas's breath visible in the cold.
            Characters present
            Tomas — POV, age 31. Independent logger working a seasonal contract. He has always treated stories of forest spirits as stories. His sister died the previous winter; he does not name this, but it shapes his stillness. Entering this beat he is tired, cold, blistered, and holding his axe. He has just felled the largest oak on the slope. He heard something cry out during the fall — first as bird, then as woman. He stood over the stump listening. He does not yet know what came out of the tree.
            Lirien — female lead. A forest fairy bound to the oak Tomas just felled. She should be dying with her tree and is not; she does not know why. She is wounded — sap-blood at her temple and at her side. She is furious and afraid, and she is trying to look dangerous because she is not. She has watched Tomas cutting for days without his knowing. She does not understand human grief as a category.
            Critical constraints on Lirien

            Do not name her species, age, or nature in prose. Tomas does not know what she is.
            Describe her only through what Tomas can observe: her wounds, her posture, the wrongness of sap on skin, the way she stands.
            She speaks plainly but formally. No thee, no thou, no inverted syntax. She is ancient but not a pastiche.

            Beat specification
            Beat 4 of 5 — "What came out of the tree"
            Target length: 700 words.
            This beat must accomplish, in order:

            Lirien emerges from the fallen trunk.
            Tomas cannot reconcile what he is seeing with what he knows. The gap plays as silence and stillness, not wonder.
            Lirien confronts him. She threatens.
            Tomas does not raise the axe.

            Emotional curve across the beat: rupture → charged stillness → threat → suspension.
            Tomas speaks at most two short lines of dialogue in this beat. Lirien carries the talking.
            End the beat with the confrontation held and unresolved. Do not let Lirien collapse in this beat — that is beat 5. End on a held moment: a line of dialogue, an image, a breath. Do not tie off.
            Prose continues from

            [Final 2-3 sentences of beat 3 pasted here verbatim. Example placeholder:]
            He lowered the axe until its head rested on the moss. The cry was still in him, threaded through the ringing in his ears, and he could not decide whether it had been a bird after all. Nothing moved on the slope. Nothing moved, and then something did.

            Continue from this point. Do not repeat these sentences. Do not summarize them. Write what comes next.
            Prohibited in this beat

            No internal monologue along the lines of maybe the old stories were true or maybe magic was real after all. Tomas's unsettling is physical and perceptual, not philosophical.
            No purple prose on Lirien's appearance. Wounds and posture first. Beauty, if it registers at all, registers after threat.
            No modern idiom. No okay, no fine, no look —.
            Do not state or hint at Lirien's species, age, or nature.
            Do not have Tomas understand what is happening. He does not understand.
            Do not resolve the confrontation.

            Output
            Prose only. ~700 words. Begin immediately.
        """

        try:
            response = client.generate(
                model=model,
                prompt=PROMPT,
                stream=False
            )
            print(PROMPT)
            print(response['response'])

        except Exception as e:
            if "model" in str(e).lower() and "not found" in str(e).lower():
                print(f"Error: Model '{model}' is not downloaded.")
                print(f"Run: docker exec ollama ollama pull {model}")
            else:
                raise





def Generate_Chapter(self):
        print("Generating")

