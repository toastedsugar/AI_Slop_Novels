from jinja2 import Environment, FileSystemLoader


def render_character_prompt(character: dict, templates_dir: str = "Templates") -> str:
    """
    Renders the CharacterPrompt.txt Jinja2 template with the given character dict.

    Args:
        character: A single character dict from blueprint.get_character() or get_characters().
        templates_dir: Path to the Templates folder (default: "Templates").

    Returns:
        The rendered prompt string, ready to pass to an LLM.

    Example:
        blueprint = Blueprint()
        character = blueprint.get_character("thistle")
        prompt = render_character_prompt(character)
    """
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("CharacterPrompt.txt")
    return template.render(character=character)


def render_system_prompt(blueprint_data: dict, templates_dir: str = "Templates") -> str:
    """
    Renders the SystemPrompt.txt Jinja2 template with blueprint data.

    Args:
        blueprint_data: The raw blueprint dict (blueprint.data).
        templates_dir: Path to the Templates folder (default: "Templates").

    Returns:
        The rendered system prompt string, ready to pass to an LLM.

    Example:
        blueprint = Blueprint()
        prompt = render_system_prompt(blueprint.data)
    """
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("SystemPrompt.txt")
    return template.render(**blueprint_data)
