import yaml
import os


class Blueprint:
    def __init__(self, path: str = 'Blueprints/Fairy and Lumberjack/main.yaml'):
        yaml.SafeLoader.add_constructor('!include', self._yaml_include)
        with open(path, 'r') as f:
            self.data = yaml.load(f, Loader=yaml.SafeLoader)

    @staticmethod
    def _yaml_include(loader, node):
        file_name = loader.construct_scalar(node)
        base_dir = os.path.dirname(loader.name)
        full_path = os.path.join(base_dir, file_name)
        with open(full_path, 'r') as f:
            return yaml.load(f, Loader=yaml.SafeLoader)

    def get_summary(self) -> str:
        return self.data['summary']

    def get_classification(self) -> dict:
        return self.data['classification']

    def get_tone(self) -> dict:
        return self.data['tone']

    def get_style(self) -> dict:
        return self.data['style']

    def get_themes(self) -> dict:
        return self.data['themes']

    def get_fantasy_framework(self) -> dict:
        return self.data['fantasy_framework']

    def get_characters(self) -> list[dict]:
        return self.data['characters']

    def get_character(self, character_id: str) -> dict | None:
        return next((c for c in self.data['characters'] if c['id'] == character_id), None)

    def get_character_relationships(self) -> list[dict]:
        return self.data['character_relationships']

    def get_chapters(self) -> list[dict]:
        return [ch['beat'] for ch in self.data['chapters']]

    def get_chapter(self, sequence: int) -> dict | None:
        return next((ch['beat'] for ch in self.data['chapters'] if ch['beat']['sequence'] == sequence), None)
