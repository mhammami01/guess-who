from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

MODEL = OllamaLLM(model="phi3")
TEMPLATE = """
Question: {question}
Answer: answer based on the question's language. Go through every step during the reply. Think about it.
"""

prompt = ChatPromptTemplate.from_template(TEMPLATE)
chain = prompt | MODEL
ai_msg = chain.invoke({"question": "Who's Spiderman?"})

print(ai_msg)