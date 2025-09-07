from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI


class LLM:

    def __init__(self, model_name: str, temperature: float = 0.0, max_tokens: int = 8192, api_key: str = None):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key


    def groq_llm(self):
        return ChatGroq(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            api_key=self.api_key
        )
    
    def openai_llm(self):
        return ChatOpenAI(
            model=self.model_name,
            #temperature=self.temperature,
            max_tokens=self.max_tokens,
            api_key=self.api_key
        )


# Create a default LLM instance
def get_llm():
    import os
    
    # Try to use GROQ first, fallback to OpenAI
    #groq_api_key = os.getenv("GROQ_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    #if groq_api_key:
    #    llm_instance = LLM(
    #        model_name="llama3-8b-8192",
    #        temperature=0.0,
    #        max_tokens=8192,
    #        api_key=groq_api_key
    #    )
    #    return llm_instance.groq_llm()
    if openai_api_key:
        llm_instance = LLM(
            model_name="gpt-3.5-turbo",
            temperature=0.0,
            max_tokens=8192,
            api_key=openai_api_key
        )
        return llm_instance.openai_llm()
    else:
        raise ValueError("No API key found. Please set either GROQ_API_KEY or OPENAI_API_KEY environment variable.")



