import os
import random
import yaml

ROUTING_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "model_routing.yaml")

def _resolve_params(config):
    resolved = {}
    for k, v in config.items():
        if isinstance(v, list) and len(v) == 2:
            resolved[k] = random.uniform(v[0], v[1])
        else:
            resolved[k] = v
    return resolved

def load_routing():
    env = os.environ.get("ENV", "dev")
    with open(ROUTING_PATH) as f:
        routing = yaml.safe_load(f)
    assert env in routing, f"ENV='{env}' not found in model_routing.yaml"
    models = routing["models"]
    tasks = routing[env]
    return {task: _resolve_params(models[alias]) for task, alias in tasks.items()}
