from linkup import LinkupClient
from pydantic import SecretStr
from typing import Literal, List
from datetime import date
from pydantic import BaseModel
from linkup.types import LinkupSourcedAnswer
from utils.pydantic_models import QuerySearchResults, QuerySubQueryResults


def get_linkup_client(api_key: SecretStr) -> LinkupClient:
    """Get the Linkup client.

    Args:
        api_key (SecretStr): The API key for the Linkup client.

    Returns:
        LinkupClient: The Linkup client.
    """
    client = LinkupClient(api_key= api_key)
    return client

def search_linkup(client: LinkupClient,
                  query: str,
                  search_mode: Literal["standard", "deep"] = "standard",
                  output_type: Literal["searchResults", "sourcedAnswer", "structured"] = "sourcedAnswer",
                  structured_output_schema: BaseModel = None,
                  from_date: date = None,
                  to_date: date = None) -> LinkupSourcedAnswer:
    """Search the Linkup client.

    Args:
        client (LinkupClient): The Linkup client.
        query: str: The query to be searched.
        search_mode: Literal["standard", "deep"] = "standard": The search mode.
        output_type: Literal["searchResults", "sourcedAnswer", "structured"] = "sourcedAnswer": Linkup output type.
        structured_output_schema: BaseModel = None: Pydantic structured output schema default to None.
        from_date: date = None: The from date default to None.
        to_date: date = None: The to date default to None.

    Returns:
        LinkupSourcedAnswer: The Linkup sourced answer.
    """
    kwargs = {
        "query": query,
        "depth": search_mode,
        "output_type": output_type,
        "structured_output_schema": structured_output_schema,
        "from_date": from_date,
        "to_date": to_date
    }
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    search_response = client.search(**kwargs)
    return search_response

def format_outputs(queries: List[str], 
                   search_results: List[LinkupSourcedAnswer],
                   search_mode: Literal["standard", "deep"] = "standard") -> QuerySubQueryResults:
    """Format the outputs.

    Args:
        queries: List[str]: The queries to be searched.
        search_results: List[LinkupSourcedAnswer]: The search results.
        search_mode: Literal["standard", "deep"] = "standard": The search mode.

    Returns:
        QuerySubQueryResults: The formatted outputs.
    """
    all_search_results = []
    for i, search_result in enumerate(search_results):
        search_result_obj = QuerySearchResults(
            query= queries[i],
            answer= search_result.answer,
            sources= search_result.sources,
            mode= search_mode
        )
        all_search_results.append(search_result_obj)
    queries_results = QuerySubQueryResults(
        main_query= all_search_results[0],
        sub_queries= all_search_results[1:]
    )
    return queries_results

def format_single_output(query: str,
                         search_result: LinkupSourcedAnswer,
                         search_mode: Literal["standard", "deep"] = "deep") -> QuerySearchResults:
    """Format the output for single call

    Args:
        query (str): query to be searched
        search_result (LinkupSourcedAnswer): Linkup search outputs
        search_mode (Literal["standard", "deep"], optional): type of search executed by linkup. Defaults to "deep".

    Returns:
        QuerySearchResults: formatted search output
    """    
    search_result_obj = QuerySearchResults(
        query= query,
        answer= search_result.answer,
        sources= search_result.sources,
        mode= search_mode
    )
    return search_result_obj