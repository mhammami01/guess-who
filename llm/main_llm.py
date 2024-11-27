from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

MODEL = OllamaLLM(model="phi3")
TEMPLATE = """
Question: {question}
Answer: answer based on the question's language. Go through every step during the reply. Think about it.
"""

def get_response(user_prompt):
    prompt = ChatPromptTemplate.from_template(TEMPLATE)
    chain = prompt | MODEL
    
    return chain.invoke(user_prompt)

ai_msg = get_response("Who's spiderman?")
print(ai_msg)