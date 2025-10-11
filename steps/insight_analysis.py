# from sambanova import SambaNova
from cerebras.cloud.sdk import Cerebras
from utils.prompts import INSIGHT_ANALYSIS_PROMPT
from utils.llm_utils import call_cerebras_model, process_reasoning_output
from utils.pydantic_models import QueryAnalysis, QueriesInsightAnalysis
import logging
from typing import List

logger = logging.getLogger(__name__)

def formulate_insight_analysis_prompt(main_question: str,
                                      generated_question: str,
                                      search_result: str):
    prompt = f"""The general question and topic of discussion is the following {main_question}.
    The generated question extracted from that main question is {generated_question}.
    Here is the internet search result for the information wanted {search_result}"""

    return prompt

def format_insights(parallelized_insight_out: List[QueryAnalysis])->QueriesInsightAnalysis:
    main_question_insights = parallelized_insight_out[0]
    generated_question_insights = parallelized_insight_out[1:]
    return QueriesInsightAnalysis(main_query= main_question_insights, generated_queries= generated_question_insights)

def insight_analysis(main_question: str, 
                     generated_question: str,
                     search_result: str,
                     client: Cerebras,
                     model_name: str
                     ) -> QueryAnalysis:
    
    logger.info(f"Analyzing generated question: {generated_question} outputs")
    system_prompt = INSIGHT_ANALYSIS_PROMPT
    prompt = formulate_insight_analysis_prompt(main_question, generated_question, search_result)
    output = call_cerebras_model(client = client,
                                  model_name= model_name,
                                  system_prompt= system_prompt,
                                  prompt= prompt
                                  )
    output_content = output.choices[0].message.content
    processed_output = process_reasoning_output(output_content)
    query_analysis_obj = QueryAnalysis(query= generated_question,
                                       search_result= search_result,
                                       analysis= processed_output)
    return query_analysis_obj