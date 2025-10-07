from utils.pydantic_models import QueryReport, QueryAnalysis, QuerySearchResults
from utils.prompts import REPORT_UPDATE_PROMPT
from utils.llm_utils import call_cerebras_model
from cerebras.cloud.sdk import Cerebras

def formulate_full_prompt(main_query:str,
                          next_query: str,
                          exisiting_report: str,
                          search_results: str,
                          analysis: str) -> str:
    full_prompt = f"""The main question in discussion is {main_query}.
    The existing report answering this query is {exisiting_report}.\n\n
    The query currently being explored to expand the report is {next_query}.
    The synthetised information from the search result is the following {search_results}.
    Here is the analysis that was done on the results: {analysis}.
    """
    return full_prompt

def report_update(report_obj: QueryReport,
                  analysis_obj: QueryAnalysis,
                  next_query: str,
                  search_results_obj: QuerySearchResults,
                  client: Cerebras,
                  model_name: str
                  ) -> QueryReport:
    main_query = report_obj.main_query
    report = report_obj.report
    analysis = analysis_obj.analysis
    search_result = search_results_obj.answer
    prompt = formulate_full_prompt(main_query= main_query,
                                   next_query= next_query,
                                   exisiting_report= report,
                                   analysis= analysis,
                                   search_results= search_result)
    system_prompt = REPORT_UPDATE_PROMPT
    output = call_cerebras_model(client = client,
                                  model_name= model_name,
                                  system_prompt= system_prompt,
                                  prompt= prompt
                                  )
    output_content = output.choices[0].message.content
    updated_report_obj = QueryReport(main_query= main_query,
                report= output_content)
    return updated_report_obj