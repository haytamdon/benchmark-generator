from concurrent.futures import ThreadPoolExecutor
from utils.pydantic_models import SubQueriesSearchMetadata, QuerySearchMetadata, QuerySubQueryResults
from datetime import date
from typing import List, Tuple, Callable
from cerebras.cloud.sdk import Cerebras
import logging

logger = logging.getLogger(__name__)

def parallel_run_metadata(function: Callable, 
                          num_max_workers: int, 
                          params: List[str], 
                          client: Cerebras, 
                          model_name: str)-> List[any]:
    """Parallel run the metadata extraction function.

    Args:
        function: The function to be run.
        num_max_workers: The number of workers to be used.
        params: The parameters to be used.
        client: The client to be used.
        model_name: The model name to be used.
    """
    with ThreadPoolExecutor(max_workers=num_max_workers) as executor:
        futures = [executor.submit(function, param, client, model_name) for param in params]
        results = [f.result() for f in futures]
    return results


def parallel_process_queries(function: Callable, 
                             num_max_workers: int, 
                             params: List[any], 
                             client: Cerebras, 
                             model_name: str):
    """Parallel process the queries processing function.

    Args:
        function: The function to be run.
        num_max_workers: The number of workers to be used.
        params: The parameters to be used.
        client: The client to be used.
        model_name: The model name to be used.
    """
    with ThreadPoolExecutor(max_workers=num_max_workers) as executor:
        futures = [executor.submit(function, param, client, model_name) for param in params]
        results = [f.result() for f in futures]
    return results

def parallel_analyze_output(function: Callable, 
                            num_max_workers: int, 
                            params: List[Tuple[any, any]], 
                            main_question: str, 
                            client: Cerebras, 
                            model_name: str):
    """Parallel process the search output analysis function.

    Args:
        function: The function to be run.
        num_max_workers: The number of workers to be used.
        params: The parameters to be used.
        client: The client to be used.
        model_name: The model name to be used.
    """
    with ThreadPoolExecutor(max_workers=num_max_workers) as executor:
        futures = [executor.submit(function, main_question, generated_question, search_result, client, model_name) for generated_question, search_result in params]
        results = [f.result() for f in futures]
    return results

def format_search_outputs(search_output: QuerySubQueryResults) -> List[Tuple[str, str]]:
    search_analysis_params = []
    first_query = search_output.main_query.query
    first_search_result = search_output.main_query.answer
    search_analysis_params.append((first_query, first_search_result))
    for sub_query in search_output.sub_queries:
        search_analysis_params.append((sub_query.query, sub_query.answer))
    return search_analysis_params

def sequential_run_search(function: Callable, 
                          params: List[Tuple[str, date, date]], 
                          client, search_mode, output_type):
    """Sequentially run the searching linkup api call.

    Args:
        function: Linkup API call function.
        num_max_workers: The number of workers to be used.
        params: The list of parameters to be used.
        client: linkup client.
        search_mode: The search mode to be used.
        output_type: The output type to be parsed.
    """
    results = []
    for query, from_date, to_date in params:
        logger.info(f"Searching: {query} ...")
        results.append(function(client, query, search_mode, output_type, None, from_date, to_date))
    return results


def format_all_questions_output(parallel_output: List[QuerySearchMetadata]) -> SubQueriesSearchMetadata:
    """Format the all questions output.

    Args:
        parallel_output: List[QuerySearchMetadata]: The parallel output.

    Returns:
        SubQueriesSearchMetadata: The formatted output.
    """
    main_query = parallel_output[0]
    sub_queries = parallel_output[1:]
    all_metadata_objects = SubQueriesSearchMetadata(
        main_query= main_query,
        sub_query_meta= sub_queries)
    return all_metadata_objects