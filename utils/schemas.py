"""
Centralized collection of schemas used throughout the deep research pipeline.

This module contains all system schemas used by LLM calls in various steps of the
research pipeline to ensure consistency and make prompt management easier.
"""
from pydantic import BaseModel, Field
from typing import List

class EnhancedSearchQuery(BaseModel):
    search_query: str = Field(...,description="The enhanced search query")
    reasoning: str = Field(..., description="Reasoning as to how the search query was generated")

class SubQuestion(BaseModel):
    sub_question: str = Field(..., description="A sub-question derived from the main question")
    reasoning: str = Field(..., description="The reasoning for why this sub-question is important")

class SubQuestionList(BaseModel):
    questions: List[SubQuestion] = Field(..., description="List of sub-questions")

class SearchDates(BaseModel):
    from_date: str = Field(..., description="Search date start")
    to_date: str = Field(..., description="Search date end")

class NextQuestion(BaseModel):
    question: str = Field(..., description="Question to be explored to supplement the report")
    reasoning: str = Field(..., description="The reasoning for why this question should be explored")

class NextQuestionList(BaseModel):
    questions: List[NextQuestion] = Field(..., description="List of next questions")

class Slide(BaseModel):
    title: str = Field(..., description="Title of the slide")
    content: str = Field(..., description="Content of the slide")
    slide_number: int = Field(..., description="Slide number or order")

class Presentation(BaseModel):
    number_of_slides: int
    slide_content: List[Slide]