from dataclasses import dataclass, field
import yaml
import os


def yaml_include(loader, node):
    # Get the filename from the YAML node
    file_name = loader.construct_scalar(node)
    
    with open(file_name, 'r') as f:
        return yaml.safe_load(f)




@dataclass
class Metadata:
    title:str
    # A mutable object like a list cannot be used as a default value directly
    # Must use field and default_factory
    genres: list[str] = field(default_factory=list)


class Blueprint:
    def __init__(self):
        # Before importing the data, validate that the data is correct and all fields are as they should be
        self.check_blueprint()

        # Register the custom tag once when the class is created
        yaml.SafeLoader.add_constructor('!include', self._yaml_include)

        print(f"Current Working Directory: {os.getcwd()}")
        print(f"Looking for file at: {os.path.abspath('../Blueprints/Romantasy/main.yaml')}")
        
        path = 'Blueprints/Romantasy/main.yaml'

        # Import blueprint data
        with open(path, 'r') as f:
            # Use the Loader we modified above
            full_blueprint = yaml.load(f, Loader=yaml.SafeLoader)

        print(full_blueprint['characters'][0]['name'])
        print("Imported Blueprint")
    








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
            # When this runs, PyYAML uses the constructor we registered in __init__
            return yaml.load(f, Loader=yaml.SafeLoader)
        

    # Do error checking to make sure blueprint is valid
    def check_blueprint(self):
        print("Checking Blueprint")

