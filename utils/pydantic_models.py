from pydantic import BaseModel, Field
from typing import List
from datetime import date
from linkup.types import LinkupSource

class SearchRequest(BaseModel):
    """Request for the search pipeline.

    This artifact is created once at the beginning of the pipeline and
    remains unchanged throughout execution.

    Attributes:
        query (str): Query to be searched.
        max_sub_questions (int): Maximum number of sub-questions to be created.
    """
    query: str
    max_sub_questions: int = 10
    max_iterations: int = 2

class QuerySubQuestions(BaseModel):
    """Immutable context containing the research query and its decomposition.

    This artifact is created once at the beginning of the pipeline and
    remains unchanged throughout execution.

    Attributes:
        main_question (str): main question.
        sub_questions (List[str]): All the questions extracted from the main question.
        justifications (List[str]): Links between the main query and the subquestions.
    """    
    main_query: str = Field(
        ..., description="The main research question from the user"
    )
    sub_questions: List[str] = Field(
        default_factory=list,
        description="Decomposed sub-questions for parallel processing",
    )
    justifications: List[str] = Field(
        default_factory= list,
        description="Links between the main query and the subquestions"
    )

class QuerySearchMetadata(BaseModel):
    """Metadata for the search query.

    Attributes:
        query (str): Query to be searched.
        from_date (date): Date from when the search should start.
        to_date (date): Date from when the search should end.
    """
    query: str = Field(
        ..., description="Query to be searched"
    )
    from_date: date = Field(
        default=None,
        description="Date from when the search should start"
    )
    to_date: date = Field(
        default=None,
        description="Date from when the search should end"
    )

class SubQueriesSearchMetadata(BaseModel):
    """Metadata for the search query.

    Attributes:
        main_query (QuerySearchMetadata): Metadata for the main query.
        sub_query_meta (List[QuerySearchMetadata]): Metadata for the sub queries.
    """
    main_query: QuerySearchMetadata
    sub_query_meta : List[QuerySearchMetadata]

class EnhancedQuerywithMetadata(BaseModel):
    original_query: str = Field(..., description="The original query")
    enhanced_query: str = Field(..., description="The enhanced query")
    from_date: date = Field(
        default=None, 
        description="The date from when the search should start"
    )
    to_date: date = Field(
        default=None, 
        description="The date from when the search should end"
    )

class EnhancedQueryList(BaseModel):
    main_query: EnhancedQuerywithMetadata
    sub_queries: List[EnhancedQuerywithMetadata]

class QuerySearchResults(BaseModel):
    """Results of the search query with the answer and the sources.

    Attributes:
        query (str): Researched Query.
        answer (str): Answer to the query.
        sources (List[LinkupSource]): Sources from where the results were extracted.
        mode (str): Search mode.
    """
    query: str = Field(..., description="Researched Query")
    answer: str = Field(..., description="Search Results in Natural Language")
    sources: List[LinkupSource] = Field(description="Sources from where the results were extracted")
    mode: str = Field(..., description="search mode")

class QuerySubQueryResults(BaseModel):
    """Results of the search query of the main query and the sub queries.

    Attributes:
        main_query (QuerySearchResults): Results of the main query.
        sub_queries (List[QuerySearchResults]): Results of the sub queries.
    """
    main_query: QuerySearchResults
    sub_queries: List[QuerySearchResults]

class QueryAnalysis(BaseModel):
    query: str = Field(..., description="researched query")
    search_result: str = Field(..., description="Search Results in Natural Language")
    analysis: str = Field(..., description="Search result analysis")

class QueriesInsightAnalysis(BaseModel):
    main_query: QueryAnalysis
    sub_queries: List[QueryAnalysis]

class QueryReport(BaseModel):
    main_query: str = Field(..., description="query to research")
    report: str = Field(..., description="generated report")

class ReportNextSteps(BaseModel):
    main_query: str = Field(..., description="original query")
    report: str = Field(..., description="generated report")
    next_questions: List[str] = Field(..., description="next queries")

class SlideOutline(BaseModel):
    main_query: str
    report: str
    outline: str

class SlideContent(BaseModel):
    slide_number: int
    slide_title: str
    slide_content: str

class PresentationContents(BaseModel):
    query: str
    num_of_slides: int
    slides: List[SlideContent]

class PresentenOutput(BaseModel):
    presentation_id : str
    file_path : str
    edit_path : str