from NovelGen import novelgen 
from blueprint import Blueprint


# import blueprint here
blueprint = Blueprint()



# Create a novelgen object that has an instance of blueprint passed to it.
novel = novelgen.NovelGen(blueprint)




OLLAMA_BASE_URL  = "http://localhost:11434"

novel.run(OLLAMA_BASE_URL)




