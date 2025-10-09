from utils.slide_utils import generate_slides, format_presenten_outputs
from utils.pydantic_models import PresentationContents, PresentenOutput
from typing import Dict

def format_slide_contents_for_prompt(content: PresentationContents) -> str:
    slide_contents = []
    for slide_content in content.slides:
        slide = f"slide number: {slide_content.slide_number} \n slide title: {slide_content.slide_title} \n slide contents: {slide_content.slide_content}"
        slide_contents.append(slide)
    str_slide_contents = "\n".join(slide_contents)
    return str_slide_contents

def formulate_slide_generation_prompt(str_slide_contents: str,
                                      company_name: str = "Haitam Solutions")-> str:
    prompt = f"generate me a benchmark presentation with tables that contains the following information: \n {str_slide_contents} by {company_name}"
    return prompt

def create_presentation(contents: PresentationContents) -> Dict[str, str]:
    str_slide_contents = format_slide_contents_for_prompt(content = contents)

    prompt = formulate_slide_generation_prompt(str_slide_contents)

    num_slides = contents.num_of_slides

    output = generate_slides(prompt, num_slides, "english", "general", "pptx")

    # presentation_obj = format_presenten_outputs(output)

    return output
