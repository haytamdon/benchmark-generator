import logging
import langchain
import json
from typing import List, Dict
from utils.prompts import QUERY_DECOMPOSITION_PROMPT
from utils.schemas import SubQuestionList
from utils.llm_utils import format_output_schema, call_cerebras_model
from utils.pydantic_models import QuerySubQuestions
from cerebras.cloud.sdk import Cerebras
from cerebras.cloud.sdk.types.chat.chat_completion import ChatCompletion

logger = logging.getLogger(__name__)

def extract_output_dict(response: ChatCompletion) -> List[Dict[str, str]]:
    """Extract the subquestions from the response

    Args:
        response (ChatCompletion): LLM output

    Returns:
        List[Dict[str, str]]: list of subquestions
    """    
    response_dict = json.loads(response.choices[0].message.content)
    question_list = response_dict["questions"]
    return question_list

def format_query_decompositon_output(question_list: Dict[str, str], 
                                     query: str) -> QuerySubQuestions:
    """format the generated subquestions

    Args:
        question_list (Dict[str, str]): list of sub-questions
        query (str): original query

    Returns:
        QuerySubQuestions: object of all the subqueries
    """    
    all_questions = []
    all_reasons = []
    for question_obj in question_list:
        question = question_obj["sub_question"]
        reason = question_obj["reasoning"]
        all_questions.append(question)
        all_reasons.append(reason)
    query_with_sub_queries = QuerySubQuestions(main_query= query,
                                               sub_questions= all_questions,
                                               justifications= all_reasons)
    return query_with_sub_queries

def generate_fallback_questions(main_query: str) -> List[Dict[str, str]]:
    """In case of an error this is a list of fallback questions to rely on

    Args:
        main_query (str): original query

    Returns:
        List[Dict[str, str]]: predifined list of subqueries
    """    
    fallback_questions = [
                            {
                                "sub_question": f"What is {main_query}?",
                                "reasoning": "Basic understanding of the topic",
                            },
                            {
                                "sub_question": f"What are the key aspects of {main_query}?",
                                "reasoning": "Exploring important dimensions",
                            },
                            {
                                "sub_question": f"What are the implications of {main_query}?",
                                "reasoning": "Understanding broader impact",
                            },
                        ]
    return fallback_questions


def query_decomposition_step(main_query: str,
                             model_name: str,
                             num_sub_questions: int,
                             client: Cerebras) -> QuerySubQuestions:
    """Step for decomposing the main query into multiple subqueries

    Args:
        main_query (str): main query to be divided
        model_name (str): name of the model
        num_sub_questions (int): number of the subquestions to be generated
        client (Cerebras): cerebras client for LLM call

    Returns:
        QuerySubQuestions: final queries object
    """
    logger.info(f"Decomposing research query: {main_query}")

    prompt_subfix = f"\nPlease generate {num_sub_questions} sub-questions."

    system_prompt = QUERY_DECOMPOSITION_PROMPT + prompt_subfix

    logger.info(f"Calling {model_name} to decompose query into {num_sub_questions} sub-questions")

    pydantic_schema = SubQuestionList.model_json_schema()

    output_schema = format_output_schema(pydantic_schema)

    try:
        output = call_cerebras_model(client, system_prompt, model_name, main_query, output_schema)
        question_list = extract_output_dict(output)
    except:
        question_list = generate_fallback_questions(main_query)

    list_of_all_questions = format_query_decompositon_output(question_list, main_query)

    return list_of_all_questions