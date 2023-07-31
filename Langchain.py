from langchain.prompts.prompt import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import os
from dotenv import load_dotenv
load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API")
template = """Imagine you are a chatbot with name ListenerAI_Bot,
      capable of providing assistance and support in multiple areas, 
      such as domestic violence reporting, mental health counseling, 
      career guidance, and emergency contacts. based on given conversation : {history} ,
      respond to user for the given input: {input}"""
    
llm = OpenAI(temperature=0.9)
PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)
conversation = ConversationChain(
    prompt=PROMPT,
    llm=llm,
    verbose=True,
    memory=ConversationBufferMemory(),
)


