from fastapi import APIRouter
from dotenv import load_dotenv
from steps.query_decomposition import query_decomposition_step
from steps.extract_metadata import metadata_extraction_step
from steps.sub_question_search import parallelize_question_search
from steps.process_queries import process_queries_step, map_queries_to_enhanced_queries, map_query_to_enhanced_query
from steps.insight_analysis import insight_analysis, format_insights
from steps.report_generation import report_generation
from steps.extract_next_questions import next_query_creation
from steps.explore_next_question import simplified_pipeline
from utils.llm_utils import get_cerebras_client, get_sambanova_client
from utils.search_utils import get_linkup_client
from utils.pydantic_models import SearchRequest, QueryReport
from utils.utils import (parallel_run_metadata, 
                         format_all_questions_output, 
                         parallel_process_queries, 
                         parallel_analyze_output,
                         format_search_outputs)
import logging
import os

logger = logging.getLogger(__name__)

load_dotenv()
router = APIRouter()

cerebras_client = get_cerebras_client(os.environ.get("CEREBRAS_API_KEY"))

linkup_client = get_linkup_client(os.environ.get("LINKUP_API_KEY"))

sambanova_client = get_sambanova_client(os.environ.get("SAMBANOVA_API_KEY"))

@router.post("/", response_model= QueryReport)
def search_pipeline(request: SearchRequest,
                    model_name: str = "llama-4-scout-17b-16e-instruct"):
    query = request.query
    max_sub_questions = request.max_sub_questions
    num_iterations = request.max_iterations
    sub_queries = query_decomposition_step(main_query= query,
                                           model_name= model_name,
                                           num_sub_questions= max_sub_questions,
                                           client= cerebras_client)
    questions = [query] + sub_queries.sub_questions
    logger.info(f"Starting the metadata extraction for {len(questions)} questions")
    results = parallel_run_metadata(function= metadata_extraction_step, 
                                    num_max_workers= max_sub_questions, 
                                    params= questions, 
                                    client= cerebras_client, 
                                    model_name= model_name)
    logger.info("Formatting the results for the main query and the sub queries")
    formatted_result = format_all_questions_output(results)
    logger.info("Starting the queries processing for the main query and the sub queries")
    enhanced_search_queries = parallel_process_queries(function= process_queries_step, 
                                    num_max_workers= max_sub_questions, 
                                    params= questions, 
                                    client= cerebras_client, 
                                    model_name= model_name)
    search_queries_with_metadata = map_queries_to_enhanced_queries(formatted_result, enhanced_search_queries)
    logger.info("Starting the question search for the main query and the sub queries")
    all_search_results = parallelize_question_search(all_questions=search_queries_with_metadata,
                                client= linkup_client)
    logger.info("Analyzing all of the outputs of the search")
    search_analysis_params = format_search_outputs(all_search_results)
    analysis = parallel_analyze_output(function= insight_analysis, 
                            num_max_workers= max_sub_questions,
                            client= cerebras_client,
                            model_name="qwen-3-235b-a22b-thinking-2507",
                            main_question= query,
                            params= search_analysis_params)
    all_queries_with_analysis = format_insights(analysis)
    logger.info("Generating Report")
    report = report_generation(queries_with_analysis= all_queries_with_analysis,
                      client= cerebras_client,
                      model_name= "qwen-3-235b-a22b-instruct-2507")
    if num_iterations<=1:
        return report
    else:
        for i in range(num_iterations-1):
            logger.info("Generating next step")
            next_queries = next_query_creation(report_obj= report,
                                num_next_questions= 5,
                                model_name=model_name,
                                client= cerebras_client)
            next_questions = next_queries.next_questions
            for qst in next_questions:
                logger.info(f"Handling next question {qst}")
                report = simplified_pipeline(query= qst,
                                            original_question= query,
                                            model_name= model_name,
                                            cerebras_client= cerebras_client,
                                            linkup_client= linkup_client,
                                            report= report)
        return report