from utils.pydantic_models import QueryReport, SlideOutline
from utils.llm_utils import call_cerebras_model
from cerebras.cloud.sdk import Cerebras
from utils.prompts import PRESENTATION_OUTLINE_GENERATION_PROMPT
import logging

logger = logging.getLogger(__name__)

def formulate_outline_prompt(report: QueryReport) -> str:
    main_question = report.main_query
    report_content = report.report
    prompt = f"""The general question and topic of discussion is the following {main_question}.
    The benchmark report for that query is: {report_content}"""
    return prompt 


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