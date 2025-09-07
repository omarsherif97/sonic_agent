
try:
    from langchain_openai import ChatOpenAI
except Exception:
    ChatOpenAI = None
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import os


def get_llm():
    """Get LLM instance with lazy initialization and safe fallbacks."""
    try:
        # Validate configuration and availability of ChatOpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL")
        if not api_key or api_key.strip() == "" or "your_openai_api_key" in api_key.lower():
            raise ValueError("OPENAI_API_KEY missing or not set in environment")

        if ChatOpenAI is None:
            raise ImportError("langchain_openai.ChatOpenAI not available")

        # Initialize real LLM client
        llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=0.0,
        )
        return llm
    except Exception as e:
        # Clear, actionable warning for operators
        print(f"Warning: Failed to initialize real LLM, using MockLLM fallback. Reason: {e}")

        # Return a mock LLM for testing and offline development
        class MockLLM:
            def invoke(self, messages):
                from langchain_core.messages import AIMessage
                return AIMessage(content="I'm a mock LLM. Please check your OPENAI_API_KEY and network connectivity.")

            def bind_tools(self, tools):
                return self

        return MockLLM()

if __name__ == "__main__":
    llm = get_llm()
    print(llm)