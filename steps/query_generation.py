import logging
import langchain
import json
from typing import List, Dict
from utils.prompts import QUERY_GENERATION_PROMPT
from utils.schemas import GeneratedQuestionList
from utils.llm_utils import format_output_schema, call_cerebras_model
from utils.pydantic_models import QueryGeneratedQuestions
from cerebras.cloud.sdk import Cerebras
from cerebras.cloud.sdk.types.chat.chat_completion import ChatCompletion

logger = logging.getLogger(__name__)

def extract_output_dict(response: ChatCompletion) -> List[Dict[str, str]]:
    """Extract the GeneratedQuestions from the response

    Args:
        response (ChatCompletion): LLM output

    Returns:
        List[Dict[str, str]]: list of GeneratedQuestions
    """    
    response_dict = json.loads(response.choices[0].message.content)
    question_list = response_dict["questions"]
    return question_list

def format_query_decompositon_output(question_list: Dict[str, str], 
                                     query: str) -> QueryGeneratedQuestions:
    """format the generated GeneratedQuestions

    Args:
        question_list (Dict[str, str]): list of generated questions
        query (str): original query

    Returns:
        QueryGeneratedQuestions: object of all the generated queries
    """    
    all_questions = []
    all_reasons = []
    for question_obj in question_list:
        question = question_obj["generated_question"]
        reason = question_obj["reasoning"]
        all_questions.append(question)
        all_reasons.append(reason)
    query_with_sub_queries = QueryGeneratedQuestions(main_query= query,
                                               sub_questions= all_questions,
                                               justifications= all_reasons)
    return query_with_sub_queries

def generate_fallback_questions(main_query: str) -> List[Dict[str, str]]:
    """In case of an error this is a list of fallback questions to rely on

    Args:
        main_query (str): original query

    Returns:
        List[Dict[str, str]]: predefined list of generated queries
    """    
    fallback_questions = [
                            {
                                "generated_question": f"What is {main_query}?",
                                "reasoning": "Basic understanding of the topic",
                            },
                            {
                                "generated_question": f"What are the key aspects of {main_query}?",
                                "reasoning": "Exploring important dimensions",
                            },
                            {
                                "generated_question": f"What are the implications of {main_query}?",
                                "reasoning": "Understanding broader impact",
                            },
                        ]
    return fallback_questions


def query_generation_step(main_query: str,
                             model_name: str,
                             num_generated_questions: int,
                             client: Cerebras) -> QueryGeneratedQuestions:
    """Step for generating from the main query multiple queries

    Args:
        main_query (str): main query to be divided
        model_name (str): name of the model
        num_generated_questions (int): number of the questions to be generated
        client (Cerebras): cerebras client for LLM call

    Returns:
        QueryGeneratedQuestions: final queries object
    """
    logger.info(f"Generating out of the research query: {main_query} multiple benchmark efficient questions")

    prompt_subfix = f"\nPlease generate {num_generated_questions} questions."

    system_prompt = QUERY_GENERATION_PROMPT + prompt_subfix

    logger.info(f"Calling {model_name} to generate out of the query {num_generated_questions} questions")

    pydantic_schema = GeneratedQuestionList.model_json_schema()

    output_schema = format_output_schema(pydantic_schema)

    try:
        output = call_cerebras_model(client, system_prompt, model_name, main_query, output_schema)
        question_list = extract_output_dict(output)
    except:
        question_list = generate_fallback_questions(main_query)

    list_of_all_questions = format_query_decompositon_output(question_list, main_query)

    return list_of_all_questions