from dataclasses import dataclass, field
import yaml
import os


def yaml_include(loader, node):
    # Get the filename from the YAML node
    file_name = loader.construct_scalar(node)
    
    with open(file_name, 'r') as f:
        return yaml.safe_load(f)

# Register the tag '!include' with the SafeLoader
yaml.SafeLoader.add_constructor('!include', yaml_include)


@dataclass
class Metadata:
    title:str
    # A mutable object like a list cannot be used as a default value directly
    # Must use field and default_factory
    genres: list[str] = field(default_factory=list)


class Blueprint:
    def __init__(self):
        # Before importing the data, validate that the data is correct and all fields are as they should be
        self.Check_Blueprint()

        # Register the custom tag once when the class is created
        yaml.SafeLoader.add_constructor('!include', self._yaml_include)




        # Import blueprint data
        with open('../Blueprints/Romantasy/main.yaml', 'r') as f:
            # Use the Loader we modified above
            full_blueprint = yaml.load(f, Loader=yaml.SafeLoader)

        print(full_blueprint['characters'][0]['name']) # Output: Alice
        print("Imported Blueprint")
    








    def yaml_include(loader, node):
        file_name = loader.construct_scalar(node)
        
        # Get the directory of the file currently being parsed
        base_dir = os.path.dirname(loader.name) 
        full_path = os.path.join(base_dir, file_name)
        
        with open(full_path, 'r') as f:
            return yaml.safe_load(f)
    

    # Do error checking to make sure blueprint is valid
    def Check_Blueprint(self):
        print("Checking Blueprint")

