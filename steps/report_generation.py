from utils.pydantic_models import QueriesInsightAnalysis, QueryReport
from utils.llm_utils import call_cerebras_model
from cerebras.cloud.sdk import Cerebras
from utils.prompts import REPORT_GENERATION_PROMPT

def formulate_main_query_subprompt(main_question: str,
                                      search_result: str,
                                      analysis: str) -> str:
    sub_prompt = f"""The general question and topic of discussion is the following {main_question}.
    Here is the internet search result for that question {search_result}
    Here is the analysis of the query with search results {analysis}
    """
    return sub_prompt

def formulate_sub_query_subprompt(generated_question: str,
                                  search_result: str,
                                  analysis: str)-> str:
    sub_prompt = f"""A sub question generated out of the main question is the following {generated_question}.
    Here is the internet search result for that question {search_result}
    Here is the analysis of the query with search results {analysis}
    """
    return sub_prompt

def formulate_prompt(queries_with_analysis: QueriesInsightAnalysis)-> str:
    main_query_with_analysis = queries_with_analysis.main_query
    main_query = main_query_with_analysis.query
    main_query_search_results = main_query_with_analysis.search_result
    main_query_analysis = main_query_with_analysis.analysis
    main_query_subprompt = formulate_main_query_subprompt(main_question= main_query,
                                                          search_result= main_query_search_results,
                                                          analysis = main_query_analysis)
    sub_queries_subprompts = []
    sub_queries_with_analysis = queries_with_analysis.sub_queries
    for sub_query_with_analysis in sub_queries_with_analysis:
        sub_query = sub_query_with_analysis.query
        sub_query_search_results = sub_query_with_analysis.search_result
        sub_query_analysis = sub_query_with_analysis.analysis
        sub_query_subprompt = formulate_sub_query_subprompt(generated_question= sub_query,
                                                            search_result= sub_query_search_results,
                                                            analysis= sub_query_analysis)
        sub_queries_subprompts.append(sub_query_subprompt)
    sub_queries_subprompt = "\n".join(sub_queries_subprompts)
    full_prompt = main_query_subprompt + "\n" + sub_queries_subprompt
    return full_prompt

def report_generation(queries_with_analysis: QueriesInsightAnalysis,
                      client: Cerebras,
                      model_name: str) -> QueryReport:
    prompt = formulate_prompt(queries_with_analysis)
    system_prompt = REPORT_GENERATION_PROMPT
    output = call_cerebras_model(client = client,
                                  model_name= model_name,
                                  system_prompt= system_prompt,
                                  prompt= prompt
                                  )
    output_content = output.choices[0].message.content
    user_query = queries_with_analysis.main_query.query
    report_obj = QueryReport(main_query= user_query,
                report= output_content)
    return report_obj