import requests
from typing import Dict
from utils.pydantic_models import PresentenOutput

def generate_slides(content, num_slides, language, template, export_type):
    response = requests.post(
        "http://localhost:4000/api/v1/ppt/presentation/generate",
        json={
            "content": content,
            "n_slides": num_slides,
            "language": language,
            "template": template,
            "export_as": export_type
        }
    )
    # print(response.json())
    return response.json()

def format_presenten_outputs(response: Dict[str, str]) -> PresentenOutput:
    presentation_id = response["presentation_id"]
    file_path = response["path"]
    edit_path = response["edit_path"]
    request_output = PresentenOutput(presentation_id= presentation_id,
                                     file_path= file_path,
                                     edit_path= edit_path)
    return request_output