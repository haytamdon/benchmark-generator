from utils.prompts import DEFAULT_SEARCH_QUERY_PROMPT
from utils.schemas import EnhancedSearchQuery
from utils.pydantic_models import EnhancedQuerywithMetadata, SubQueriesSearchMetadata, EnhancedQueryList, QuerySearchMetadata
from utils.llm_utils import format_output_schema, call_cerebras_model
from cerebras.cloud.sdk import Cerebras
import logging
import json
from datetime import date
from typing import List
logger = logging.getLogger(__name__)

def extract_output_dict(response) -> EnhancedSearchQuery:
    response_dict = json.loads(response.choices[0].message.content)
    search_query = response_dict["search_query"]
    reasoning = response_dict["reasoning"]
    return EnhancedSearchQuery(search_query=search_query, reasoning=reasoning)

def fallback_search_query_outputs(query) -> EnhancedSearchQuery:
    return EnhancedSearchQuery(search_query=query, reasoning="No search query was generated")

def add_metadata_to_query(query: str, search_query: str, from_date: date, to_date: date) -> EnhancedQuerywithMetadata:
    kwargs = {
        "original_query" : query,
        "enhanced_query" : search_query,
        "from_date" : from_date,
        "to_date" : to_date
    }
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    return EnhancedQuerywithMetadata(**kwargs)

def map_query_to_enhanced_query(query_with_metadata: QuerySearchMetadata,
                                enhanced_query: EnhancedSearchQuery)-> EnhancedQuerywithMetadata:
    main_query = query_with_metadata.query
    enhanced_main_query = enhanced_query.search_query
    from_date = query_with_metadata.from_date
    to_date = query_with_metadata.to_date
    search_query_with_metadata = add_metadata_to_query(main_query, enhanced_main_query, from_date, to_date)
    return search_query_with_metadata
    

def map_queries_to_enhanced_queries(queries_with_metadata: SubQueriesSearchMetadata, 
                                    enhanced_queries: List[EnhancedSearchQuery]) -> EnhancedQueryList:
    all_queries_with_metadata_list = []
    main_query = queries_with_metadata.main_query.query
    enhanced_main_query = enhanced_queries[0].search_query
    from_date = queries_with_metadata.main_query.from_date
    to_date = queries_with_metadata.main_query.to_date
    main_search_query_with_metadata = add_metadata_to_query(main_query, enhanced_main_query, from_date, to_date)
    sub_queries_with_metadata = queries_with_metadata.sub_query_meta
    for i in range(1,len(enhanced_queries)):
        enhanced_sub_query = enhanced_queries[i].search_query
        sub_query = sub_queries_with_metadata[i-1].query
        from_date = sub_queries_with_metadata[i-1].from_date
        to_date = sub_queries_with_metadata[i-1].to_date
        all_queries_with_metadata_list.append(add_metadata_to_query(sub_query, enhanced_sub_query, from_date, to_date))
    search_queries_obj = EnhancedQueryList(
        main_query= main_search_query_with_metadata,
        sub_queries= all_queries_with_metadata_list
    )
    return search_queries_obj


def process_queries_step(query: str, 
                             client: Cerebras,
                             model_name: str,
                             current_date: date = date.today())-> EnhancedSearchQuery:
    
    logger.info(f"Processing query: {query}")
    prompt_subfix = f"\nFor more details here is the current date {current_date}."
    system_prompt = DEFAULT_SEARCH_QUERY_PROMPT + prompt_subfix

    pydantic_schema = EnhancedSearchQuery.model_json_schema()

    output_schema = format_output_schema(pydantic_schema)

    try:
        output = call_cerebras_model(client, system_prompt, model_name, query, output_schema)
        enhanced_search_query = extract_output_dict(output)
    except:
        enhanced_search_query = fallback_search_query_outputs(query)

    return enhanced_search_query

