from openai import OpenAI
import yaml

def get_config_by_model(model_name):
    """Read the configuration of the specified model from the YAML file"""
    with open("config.yaml", "r", encoding="utf-8") as f:
        full_config = yaml.safe_load(f)
    model_config = full_config.get("models", {}).get(model_name)
    if not model_config:
        raise ValueError(f"The configuration for the model {model_name} was not found in config.yaml.")
    return model_config

def call_api(model_name, system_prompt: str, user_prompt, text: str):
    model_config = get_config_by_model(model_name)
    client = OpenAI(
        api_key=model_config["api_key"],
        base_url=model_config["base_url"],
    )
    user_prompt = user_prompt + text

    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]

    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        response_format={
            'type': 'json_object'
        }
    )
    return response.choices[0].message.content

# API for specifying the model to be used in repair agent calls
def call_api_round2(model_name, system_prompt: str, user_prompt, text: str, result, conflict_terms):
    model_config = get_config_by_model(model_name)
    client = OpenAI(
        api_key=model_config["api_key"],
        base_url=model_config["base_url"],
    )
    user_prompt = user_prompt + text

    with open("resources/prompts/fixUserPrompt1.txt", "r", encoding="utf-8") as sf:
        second_round_prompt_1 = sf.read()
    with open("resources/prompts/fixUserPrompt2.txt", "r", encoding="utf-8") as sf:
        second_round_prompt_2 = sf.read()

    second_round_prompt = second_round_prompt_1 + str(conflict_terms) + second_round_prompt_2

    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": result},
                {"role": "user", "content": second_round_prompt}]

    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        response_format={
            'type': 'json_object'
        }
    )
    return response.choices[0].message.content
