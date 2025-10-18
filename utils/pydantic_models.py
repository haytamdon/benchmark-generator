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

class QueryGeneratedQuestions(BaseModel):
    """Immutable context containing the research query and its decomposition.

    This artifact is created once at the beginning of the pipeline and
    remains unchanged throughout execution.

    Attributes:
        main_question (str): main question.
        sub_questions (List[str]): All the questions extracted from the main question.
        justifications (List[str]): Links between the main query and the GeneratedQuestions.
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
        description="Links between the main query and the GeneratedQuestions"
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
    """Enhanced query with metadata.

    Attributes:
        original_query (str): The original query.
        enhanced_query (str): The enhanced query.
        from_date (date): Optional start date for the search.
        to_date (date): Optional end date for the search.
    """
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
    """Container for a main enhanced query and the enhanced sub‑queries with their metadata.

    Attributes:
        main_query (EnhancedQuerywithMetadata): The primary enhanced query.
        sub_queries (List[EnhancedQuerywithMetadata]): List of enhanced sub‑queries.
    """
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
    """Analysis of a single query's search result.

    Attributes:
        query (str): The researched query.
        search_result (str): The raw search result text.
        analysis (str): Interpretation or insights derived from the result.
    """
    query: str = Field(..., description="researched query")
    search_result: str = Field(..., description="Search Results in Natural Language")
    analysis: str = Field(..., description="Search result analysis")

class QueriesInsightAnalysis(BaseModel):
    """Aggregated analysis for a main query and its sub‑queries.

    Attributes:
        main_query (QueryAnalysis): Analysis of the main query.
        sub_queries (List[QueryAnalysis]): Analyses of each sub‑query.
    """
    main_query: QueryAnalysis
    sub_queries: List[QueryAnalysis]

class QueryReport(BaseModel):
    """Generated report for a query.

    Attributes:
        main_query (str): The query that was researched.
        report (str): The generated report content.
    """
    main_query: str = Field(..., description="query to research")
    report: str = Field(..., description="generated report")

class ReportNextSteps(BaseModel):
    """Next steps derived from a generated report.

    Attributes:
        main_query (str): The original query.
        report (str): The generated report content.
        next_questions (List[str]): Suggested follow‑up questions.
    """
    main_query: str = Field(..., description="original query")
    report: str = Field(..., description="generated report")
    next_questions: List[str] = Field(..., description="next queries")

class SlideOutline(BaseModel):
    """Outline structure for a presentation slide deck.

    Attributes:
        main_query (str): The primary query the slides address.
        report (str): The report content to be summarized.
        outline (str): Textual outline of the slide deck.
    """
    main_query: str
    report: str
    outline: str

class SlideContent(BaseModel):
    """Content for an individual slide.

    Attributes:
        slide_number (int): The slide's sequential number.
        slide_title (str): Title of the slide.
        slide_content (str): Body text or markdown for the slide.
    """
    slide_number: int
    slide_title: str
    slide_content: str

class PresentationContents(BaseModel):
    """Complete set of presentation data.

    Attributes:
        query (str): The original query driving the presentation.
        num_of_slides (int): Total number of slides.
        slides (List[SlideContent]): List of slide contents.
    """
    query: str
    num_of_slides: int
    slides: List[SlideContent]

class PresentenOutput(BaseModel):
    """Output information for a generated presentation.

    Attributes:
        presentation_id (str): Identifier of the created presentation.
        file_path (str): Path to the presentation file.
        edit_path (str): Path to the editable version of the presentation.
    """
    presentation_id : str
    file_path : str
    edit_path : str

class Criterion(BaseModel):
    """Single evaluation criterion.

    Attributes:
        criterion_name (str): Name of the criterion used for evaluation.
        nature (str): Type of criterion (Quantitative or Qualitative).
        reasoning (str): Explanation for why this criterion was chosen.
    """
    criterion_name: str = Field(..., description="name of the criterion based on which we are evaluating the identified tools")
    nature: str = Field(..., description="Type of criterion Quantitive or Qualitative")
    reasoning: str = Field(..., description="Reasoning as to why this criterion was chosen")

class Criteria(BaseModel):
    """Collection of evaluation criteria for a query.

    Attributes:
        query (str): The query being evaluated.
        list_of_criteria (List[Criterion]): List of criteria objects.
    """
    query: str
    list_of_criteria: List[Criterion] = Field(..., description="list of all the criteria for evaluation")

class FirstShortList(BaseModel):
    benchmark_topic: str = Field(..., description="The question for the benchmark")
    extracted_shortlist: List[str] = Field(..., description="Extracted subjects for benchmark")