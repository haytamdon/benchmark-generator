from utils.prompts import EVALUATION_CRITERIA_PROMPT
from utils.pydantic_models import Criteria, Criterion
from utils.schemas import CriteriaList
from utils.llm_utils import format_output_schema, call_cerebras_model
from cerebras.cloud.sdk import Cerebras
from cerebras.cloud.sdk.types.chat.chat_completion import ChatCompletion
import json

def extract_output_dict(response: ChatCompletion, query: str) -> Criteria:
    """Extract the GeneratedQuestions from the response

    Args:
        response (ChatCompletion): LLM output

    Returns:
        List[Dict[str, str]]: list of GeneratedQuestions
    """    
    response_dict = json.loads(response.choices[0].message.content)
    list_of_criteria = response_dict["list_of_criteria"]
    formatted_list = [Criterion(
        criterion_name= crit["criterion_name"],
        nature= crit["nature"],
        reasoning= crit["reasoning"]
    ) for crit in list_of_criteria]
    criteria_obj = Criteria(
        query= query,
        list_of_criteria= formatted_list
    )
    return criteria_obj

def define_evaluation_criteria(client: Cerebras, model_name: str, main_query: str) -> Criteria:
    system_prompt = EVALUATION_CRITERIA_PROMPT
    pydantic_schema = CriteriaList.model_json_schema()
    output_schema = format_output_schema(pydantic_schema)
    output = call_cerebras_model(client, system_prompt, model_name, main_query, output_schema)
    list_of_criteria = extract_output_dict(output)
    return list_of_criteria