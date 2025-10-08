from utils.pydantic_models import QueryReport, SlideOutline, SlideContent, PresentationContents
from utils.llm_utils import call_cerebras_model, format_output_schema
from utils.schemas import Presentation
from cerebras.cloud.sdk import Cerebras
from utils.prompts import PRESENTATION_OUTLINE_GENERATION_PROMPT, PRESENTATION_CONTENT_GENERATION_PROMPT
import logging
import json

logger = logging.getLogger(__name__)

def formulate_outline_prompt(report: QueryReport) -> str:
    main_question = report.main_query
    report_content = report.report
    prompt = f"""The general question and topic of discussion is the following {main_question}.
    The benchmark report for that query is: {report_content}"""
    return prompt 

def formulate_content_prompt(outline: SlideOutline)-> str:
    prompt = f"""Here is the outline in question {outline.outline}
    and here is the benchmark report from where to get the content"""
    return prompt

def extract_output_dict(response, outline: SlideOutline) -> PresentationContents:
    response_dict = json.loads(response.choices[0].message.content)
    num_of_slides = response_dict["number_of_slides"]
    list_of_slides = response_dict["slide_content"]
    formatted_list_of_slides = [SlideContent(slide_content = slide["content"],
                                             slide_number= slide["slide_number"],
                                             slide_title = slide["title"]) for slide in list_of_slides]
    return PresentationContents(query= outline.main_query, num_of_slides= num_of_slides, slides= formatted_list_of_slides)


def slide_outline_generation(report: QueryReport,
                      client: Cerebras,
                      num_of_slides: int,
                      model_name: str) -> SlideOutline:
    prompt_subfix = f"\nPlease generate {num_of_slides} slides."
    system_prompt = PRESENTATION_OUTLINE_GENERATION_PROMPT + prompt_subfix
    prompt = formulate_outline_prompt(report)

    output = call_cerebras_model(client = client,
                                  model_name= model_name,
                                  system_prompt= system_prompt,
                                  prompt= prompt
                                  )
    output_content = output.choices[0].message.content
    outline_obj = SlideOutline(main_query=report.main_query,
                               report= report.report,
                               outline=output_content)
    return outline_obj

def slides_content_generation(client: Cerebras,
                              outline: SlideOutline,
                              model_name: str) -> PresentationContents:
    system_prompt = PRESENTATION_CONTENT_GENERATION_PROMPT
    prompt = formulate_content_prompt(outline)

    output = call_cerebras_model(client= client,
                                 model_name= model_name,
                                 system_prompt= system_prompt,
                                 prompt= prompt)
    
    pydantic_schema = Presentation.model_json_schema()

    output_schema = format_output_schema(pydantic_schema)

    output = call_cerebras_model(client, system_prompt, model_name, prompt, output_schema)

    presentation_contents = extract_output_dict(output, outline)

    return presentation_contents
