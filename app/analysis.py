
import json
import os
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from decouple import config


llm_agent = None
try:
    openrouter_api_key = config('OPENROUTER_API_KEY')
    if not openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set.")
    openrouter_model = config('OPENROUTER_MODEL')

    llm_agent = Agent(
        OpenAIModel(
            model_name=openrouter_model,
            provider=OpenRouterProvider(api_key=openrouter_api_key)
        ),
        name="interviewer",
        system_prompt='You are an expert interviewer and provide concise, helpful feedback.'
    )
    print("Pydantic-AI agent initialized successfully.")
except Exception as e:
    print(f"Pydantic-AI agent initialization failed: {e}. Using dummy LLM functions.")


async def get_feedback_from_llm(llm_agent: Agent, job_title: str, topic: str, question: str, answer: str) -> str:
    """
    Generates feedback for a given question and answer using an LLM.
    (This is a placeholder).
    """
    if llm_agent:
        # Assuming pydantic_ai.Agent has a method like generate_feedback
        prompt = f"Given the job title: {job_title}, topic: {topic}, and the interview question: '{question}', provide feedback on the following answer: '{answer}'. Focus on clarity, relevance, completeness, and suggest a good answer. Return only the feedback content without any prefix."
        result = await llm_agent.run(prompt)
        feedback = result.output
        # Clean up any remaining prefixes
        if feedback.startswith("**Feedback:**"):
            feedback = feedback.replace("**Feedback:**", "").strip()
        elif feedback.startswith("**Feedback**"):
            feedback = feedback.replace("**Feedback**", "").strip()
        elif feedback.startswith("Feedback:"):
            feedback = feedback.replace("Feedback:", "").strip()
        return feedback
    else:
        return f"**Dummy Feedback for {job_title} Interview on {topic}**\n\n*   **Clarity:** Good (dummy feedback)\n*   **Relevance:** Seems relevant to '{question}' (dummy feedback)\n*   **Completeness:** Appears complete (dummy feedback)\n*   **Suggested Improvement:** Consider mentioning specific examples (dummy feedback)."


async def analyze_answer(job_title: str, topic: str, question: str, transcription: str, llm_agent: Agent = llm_agent) -> dict:
    """
    Analyzes the user's answer and provides feedback.
    """
    if not transcription or len(transcription.split()) < 5:
        return "clarity Could be clearer. The answer is very short. relevance Not applicable."

    return await get_feedback_from_llm(llm_agent, job_title, topic, question, transcription)


async def generate_question_with_llm(job_title: str, topic: str, llm_agent: Agent = llm_agent) -> str:
    """
    Generates an interview question using an LLM.
    (This is a placeholder).
    """
    if llm_agent:
        prompt = f"Generate a short interview question for a {job_title} position, focusing on the topic of {topic}. Return only the question text without any prefix or formatting."
        result = await llm_agent.run(prompt)
        question = result.output
        # Clean up any remaining prefixes
        if question.startswith("**Question:**"):
            question = question.replace("**Question:**", "").strip()
        elif question.startswith("Question:"):
            question = question.replace("Question:", "").strip()
        return question
    else:
        # In the future, this will call an actual LLM.
        return f"This is a dummy question about {topic} for a {job_title}."


async def get_interview_question(job_title: str, topic: str = None) -> str:
    """
    Returns an interview question based on the job title and topic.
    """
    if not topic:
        topic = "general"
    return await generate_question_with_llm(job_title, topic)
