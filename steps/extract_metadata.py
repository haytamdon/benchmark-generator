from datetime import date, datetime
from cerebras.cloud.sdk import Cerebras
from utils.prompts import METADATA_EXTRACTION_PROMPT
from utils.pydantic_models import QuerySearchMetadata
from utils.schemas import SearchDates
import logging
from utils.llm_utils import format_output_schema, call_cerebras_model
from typing import Tuple
import json

logger = logging.getLogger(__name__)

def fallback_date_outputs(query) -> QuerySearchMetadata:
    metadata_object = QuerySearchMetadata(query=query)
    return metadata_object

def format_metadata_types(to_date: str, from_date: str) -> Tuple[date, date]:
    if to_date == "None":
        to_date = None
    else:
        to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
    if from_date == "None":
        from_date = None
    else:
        from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
    return to_date, from_date
    

def extract_output_dict(response, query) -> QuerySearchMetadata:
    response_dict = json.loads(response.choices[0].message.content)
    to_date = response_dict['to_date']
    from_date = response_dict['from_date']
    to_date, from_date = format_metadata_types(to_date, from_date)
    metadata_object = QuerySearchMetadata(query=query,
                                          from_date= from_date,
                                          to_date= to_date)
    return metadata_object

def metadata_extraction_step(query: str, 
                             client: Cerebras,
                             model_name: str,
                             current_date: date = date.today())-> QuerySearchMetadata:
    
    logger.info(f"Decomposing research query: {query}")
    prompt_subfix = f"\nFor more details here is the current date {current_date}."
    system_prompt = METADATA_EXTRACTION_PROMPT + prompt_subfix

    pydantic_schema = SearchDates.model_json_schema()

    output_schema = format_output_schema(pydantic_schema)

    try:
        output = call_cerebras_model(client, system_prompt, model_name, query, output_schema)
        query_metadata_obj = extract_output_dict(output, query)
    except:
        query_metadata_obj = fallback_date_outputs(query)

    return query_metadata_obj