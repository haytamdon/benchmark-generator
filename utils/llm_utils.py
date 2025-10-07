"""
Collection of functions for calling LLMs and tools throughout the pipeline
"""
from cerebras.cloud.sdk import Cerebras
import os
from pydantic import SecretStr
from typing import Dict
from sambanova import SambaNova
from cerebras.cloud.sdk.types.chat.chat_completion import ChatCompletion


def get_cerebras_client(api_key: SecretStr = SecretStr(os.environ.get("CEREBRAS_API_KEY"))):
    """Get the Cerebras client.

    Args:
        api_key (SecretStr): The API key for the Cerebras client.

    Returns:
        Cerebras: The Cerebras client.
    """
    client = Cerebras(
        api_key= api_key
    )
    return client

def get_sambanova_client(api_key: SecretStr = SecretStr(os.environ.get("SAMBANOVA_API_KEY")),
                         api_endpoint: str = "https://api.sambanova.ai/v1") -> SambaNova:
    """Get the Sambanova client.

    Args:
        api_key (SecretStr, optional): Sambanova API key.
        api_endpoint (str, optional): Sambanova's base URL.

    Returns:
        SambaNova: SambaNova Client
    """
    client = SambaNova(
        api_key= api_key,
        base_url= api_endpoint,
    )
    return client

def call_cerebras_model(client: Cerebras, 
                        system_prompt: str, 
                        model_name: str, 
                        prompt: str, 
                        response_schema: Dict[str, any] = None) -> ChatCompletion:
    """Call the Cerebras model.

    Args:
        client (Cerebras): The Cerebras client.
        system_prompt (str): The system prompt.
        model_name (str): The name of the model to be used.
        prompt (str): The prompt.
        response_schema (Dict[str, any]): The response schema.

    Returns:
        Completion: The completion of the model.
    """
    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        response_format= response_schema
    )
    return completion

def call_sambanova_model(client: SambaNova, 
                         model_name: str, 
                         system_prompt: str, 
                         prompt: str,
                         temperature: float = 0.1,
                         top_p: float = 0.1) -> str:
    """Call a sambanova model

    Args:
        client (SambaNova): SambaNova Client
        model_name (str): Name of the model
        system_prompt (str): system prompt
        prompt (str): prompt to answer
        temperature (float, optional): model temperature. Defaults to 0.1.
        top_p (float, optional): top-p sampling. Defaults to 0.1.

    Returns:
        str: Model output
    """    
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role":"system","content":system_prompt},
            {"role":"user","content":prompt}
            ],
        temperature= temperature,
        top_p= top_p
    )
    return response.choices[0].message.content

def process_reasoning_output(response: str) -> str:
    """For reasoning model outputs extracting only the actual answer without the reasoning

    Args:
        response (str): reasoning model output

    Returns:
        str: reasoning model answer without the reasoning
    """    
    if "</think>" in response:
        processed_response = response.split("</think>")[1].strip()
    else:
        processed_response = response
    return processed_response

def format_output_schema(pydantic_json: Dict[str, any]) -> Dict[str, any]:
    """Format the output schema.

    Args:
        pydantic_json (Dict[str, any]): The Pydantic JSON schema.

    Returns:
        Dict[str, any]: The formatted schema.
    """
    format_schema = {
                        "type": "json_schema", 
                        "json_schema": {
                            "name": "question_schema",
                            "strict": True,
                            "schema": pydantic_json
                        }
                    }
    return format_schema