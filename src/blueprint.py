from dataclasses import dataclass, field
import yaml
import os


@dataclass
class Noveldata:
    title:str
    author:str
    target_word_count: int
    target_word_count_minimum: int
    target_word_count_maximum: int
    perspective: str
    tense: str

    genres: list[str]
    tone: list[str]
    summary: str
    characters: list[str]
    chapters: list[str]
    character_relationships: list[str]
    chapters: list[str]

@dataclass
class Character:
    name: str
    role: str
    personality: list[str]

@dataclass
class Chapter:
    name: str

@dataclass
class Character_Relationships:
    name: str

class Blueprint:
    def __init__(self):
        # Before importing the data, validate that the data is correct and all fields are as they should be
        self.check_blueprint()

        # Register the custom tag once when the class is created
        yaml.SafeLoader.add_constructor('!include', self._yaml_include)

        print(f"Current Working Directory: {os.getcwd()}")
        print(f"Looking for file at: {os.path.abspath('../Blueprints/Romantasy/main.yaml')}")

        path = 'Blueprints/Romantasy/main.yaml'

        self.full_blueprint = self.get_blueprint(path)
        print("Blueprint Loaded")


    # This is the logic that 'main.yaml' will trigger
    @staticmethod
    def _yaml_include(loader, node):
        file_name = loader.construct_scalar(node)
        
        # loader.name is inherited from the 'with open' call below
        base_dir = os.path.dirname(loader.name) 
        full_path = os.path.join(base_dir, file_name)
        
        with open(full_path, 'r') as f:
            return yaml.load(f, Loader=yaml.SafeLoader)
    

    # 3. This is your main execution method
    def get_blueprint(self, path):
        with open(path, 'r') as f:
            raw_dict = yaml.load(f, Loader=yaml.SafeLoader)
        
        # Store the object directly in the class attribute
        self.full_blueprint = Noveldata(**raw_dict)
        
        # Return it just in case you want to use it elsewhere
        return self.full_blueprint
        

    # Do error checking to make sure blueprint is valid
    def check_blueprint(self):
        print("Checking Blueprint")

    def print_blueprint(self):
        print(self.full_blueprint)
