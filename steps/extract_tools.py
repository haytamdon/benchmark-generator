from utils.prompts import TOOLS_EXTRACTION_PROMPT
from utils.schemas import BenchmarkSubjectList
from utils.pydantic_models import QuerySubQueryResults, FirstShortList
from utils.llm_utils import format_output_schema, call_cerebras_model
from cerebras.cloud.sdk import Cerebras
from cerebras.cloud.sdk.types.chat.chat_completion import ChatCompletion
import json

def format_extracted_outputs(response: ChatCompletion, query: str) -> FirstShortList:
    """Extract the BenchmarkSubjectList from the response

    Args:
        response (ChatCompletion): LLM output
        query (str): The original query

    Returns:
        dict: Dictionary containing the list of benchmark subjects
    """    
    response_dict = json.loads(response.choices[0].message.content)
    list_of_subjects = response_dict["list_of_subjects"]
    list_of_subject_names = [subject["subject_name"] for subject in list_of_subjects]
    short_list = FirstShortList(benchmark_topic= query,
                                extracted_shortlist= list_of_subject_names)
    return short_list

def formulate_tool_extraction_prompt(search_results_with_queries: QuerySubQueryResults):
    main_query = search_results_with_queries.main_query
    sub_queries_with_search_results = search_results_with_queries.sub_queries
    search_results = [search.answer for search in sub_queries_with_search_results]
    search_results_str = "\n".join(search_results)
    prompt = f"""The general question and topic of discussion is the following {main_query}.
    Here are all of the internet search results of all the subquestionss {search_results_str}"""
    return prompt


def extract_benchmark_subjects(client: Cerebras, model_name: str, search_results_with_queries: QuerySubQueryResults) -> FirstShortList:
    """Extract benchmark subjects from search results

    Args:
        client (Cerebras): Cerebras client instance
        model_name (str): Name of the model to use
        main_query (str): The main benchmark topic/query
        search_results (str): Search results from multiple subqueries

    Returns:
        dict: Dictionary containing the extracted benchmark subjects
    """
    main_query = search_results_with_queries.main_query.query
    system_prompt = TOOLS_EXTRACTION_PROMPT
    pydantic_schema = BenchmarkSubjectList.model_json_schema()
    output_schema = format_output_schema(pydantic_schema)
    
    # Combine the main query with search results for context
    user_prompt = formulate_tool_extraction_prompt(search_results_with_queries)
    
    output = call_cerebras_model(client, system_prompt, model_name, user_prompt, output_schema)
    benchmark_subjects = format_extracted_outputs(output, main_query)
    return benchmark_subjects
