from dataclasses import dataclass, field

@dataclass
class Metadata:
    title:str
    # A mutable object like a list cannot be used as a default value directly
    # Must use field and default_factory
    genres: list[str] = field(default_factory=list)

class Blueprint:
    def __init__(self):
        print("Creating Blueprint")