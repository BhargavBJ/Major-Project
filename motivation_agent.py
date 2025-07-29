from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
import random

# Load variables from .env file
load_dotenv()
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

# Create and configure model only once
chat = ChatGroq(
    temperature=0.2,
    model_name="llama-3.1-8b-instant",
    groq_api_key=GROQ_API_KEY
)

# Static system prompt

# Prompt variations


def generate_motivational_quote(topic: str = None, stream: bool = False):
    """
    Generate a motivational quote, optionally related to a topic.
    
    Args:
        topic (str, optional): The health-related topic to focus on (e.g., 'cancer', 'resilience').
        stream (bool): If True, stream the quote in real-time.

    Returns:
        str: The motivational quote (unless streamed).
    """
    system_prompt = "You are a compassionate assistant who provides short, uplifting motivational quotes to inspire people on their health journey."

    user_prompts = [
    "Share a motivational quote for someone recovering from illness.",
    "Give an inspiring message for a person starting their fitness journey.",
    "What is a good motivational quote for healthy living?",
    "Say something encouraging to boost someone's mental health.",
    "Provide a powerful quote for someone striving to improve their lifestyle.",
    ]
    if topic:
        human = "Share a motivational quote related to: {topic}"
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human)
        ])
        chain = prompt | chat

        if stream:
            for chunk in chain.stream({"topic": topic}):
                print(chunk.content, end="", flush=True)
        else:
            response = chain.invoke({"topic": topic})
            return response.content
    else:
        human = random.choice(user_prompts)
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human)
        ])
        chain = prompt | chat

        if stream:
            for chunk in chain.stream({}):
                print(chunk.content, end="", flush=True)
        else:
            response = chain.invoke({})
            return response.content

print(generate_motivational_quote(topic="health"))