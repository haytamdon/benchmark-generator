from utils.pydantic_models import QueryReport, ReportNextSteps
from utils.prompts import NEXT_QUESTIONS_PROMPT
from utils.schemas import NextQuestionList, NextQuestion
from utils.llm_utils import format_output_schema, call_cerebras_model
import logging
from cerebras.cloud.sdk import Cerebras
from typing import List, Dict
import json

logger = logging.getLogger(__name__)

def extract_output_dict(response) -> List[Dict[str, str]]:
    response_dict = json.loads(response.choices[0].message.content)
    question_list = response_dict["questions"]
    return question_list

def format_query_decompositon_output(question_list, query, report) -> ReportNextSteps:
    all_questions = []
    for question_obj in question_list:
        question = question_obj["question"]
        all_questions.append(question)
    query_with_sub_queries = ReportNextSteps(main_query= query,
                                               next_questions= all_questions,
                                               report= report)
    return query_with_sub_queries

def next_query_creation(report_obj: QueryReport,
                        num_next_questions: int,
                        model_name: str,
                        client: Cerebras) -> ReportNextSteps:
    report = report_obj.report

    original_question = report_obj.main_query

    prompt_subfix = f"\nPlease generate {num_next_questions} questions to be explored."

    system_prompt = NEXT_QUESTIONS_PROMPT + prompt_subfix

    logger.info(f"Calling {model_name} to generate {num_next_questions} questions to be explored")

    pydantic_schema = NextQuestionList.model_json_schema()

    output_schema = format_output_schema(pydantic_schema)

    output = call_cerebras_model(client, system_prompt, model_name, report, output_schema)

    question_list = extract_output_dict(output)

    next_queries_obj = format_query_decompositon_output(question_list, original_question, report)
    
    return next_queries_obj