from steps.extract_metadata import metadata_extraction_step
from steps.process_queries import process_queries_step, map_query_to_enhanced_query
from steps.update_report import report_update
from utils.search_utils import search_linkup, format_single_output
from utils.pydantic_models import QueryReport
from steps.insight_analysis import insight_analysis
from cerebras.cloud.sdk import Cerebras
from linkup import LinkupClient

def simplified_pipeline(query: str, 
                        original_question: str, 
                        model_name: str, 
                        cerebras_client: Cerebras, 
                        linkup_client: LinkupClient, 
                        report: QueryReport) -> QueryReport:
    results = metadata_extraction_step(query= query,
                                       client= cerebras_client,
                                       model_name= model_name)
    # formatted_result = format_all_questions_output([results])
    enhanced_search_query = process_queries_step(query= query,
                         client= cerebras_client,
                         model_name= model_name)
    search_query_with_metadata = map_query_to_enhanced_query(results, enhanced_search_query)
    search_result = search_linkup(client= linkup_client,
                  query= search_query_with_metadata.enhanced_query,
                  search_mode= 'deep',
                  from_date= search_query_with_metadata.from_date,
                  to_date= search_query_with_metadata.to_date
                  )
    search_analysis_param = format_single_output(query= query,
                         search_result= search_result)
    analysis = insight_analysis(main_question=original_question,
                                sub_question= query,
                                search_result= search_analysis_param.answer,
                                client= cerebras_client,
                                model_name="qwen-3-235b-a22b-thinking-2507")
    updated_report = report_update(report_obj= report,
                                   analysis_obj= analysis,
                                   next_query= query,
                                   search_results_obj= search_analysis_param,
                                   client= cerebras_client,
                                   model_name="qwen-3-235b-a22b-instruct-2507")
    return updated_report
    