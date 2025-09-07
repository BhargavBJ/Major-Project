from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
import random

load_dotenv()
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

chat = ChatGroq(
    temperature=0.8,
    model_name="llama-3.1-8b-instant",
    groq_api_key=GROQ_API_KEY
)

def generate_motivational_quote(topic: str = None, stream: bool = False):
    system_prompt = (
        "You are a compassionate assistant who provides short, uplifting, and unique motivational quotes "
        "to inspire people on their health journey. Always generate a fresh quote and avoid repeating previous ones. "
        "Be original and emotionally resonant."
    )

    user_prompts = [
        "What's a fresh motivational message for someone working on their physical health?",
        "Give a unique inspiring quote for a patient recovering from illness.",
        "Share a new quote that encourages mental wellness and balance.",
        "Offer a fresh, hopeful quote for someone starting a healthier lifestyle.",
        "Inspire someone with a non-cliché quote about health or strength.",
    ]

    if topic:
        human = f"Provide a new motivational quote related to {topic} that hasn't been used before."
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

if __name__ == "__main__":
    print(generate_motivational_quote())
