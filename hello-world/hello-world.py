import os
import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
# from llama_index.graph_stores.neo4j import Neo4jGraphStore
from neo4j import GraphDatabase
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langsmith import traceable
from dotenv import load_dotenv

load_dotenv()

chroma_client = chromadb.HttpClient(
    host=os.getenv("CHROMADB_HOST"),
    port=os.getenv("CHROMADB_PORT"),
    ssl=False,
    headers=None,
    settings=Settings(),
    tenant=DEFAULT_TENANT,
    database=DEFAULT_DATABASE,
)
# 
collection = chroma_client.get_collection("project_knowledge")

chromadb_result = collection.query(
    query_texts=["What is the AI Chatbot project about?"],
    # query_texts=["What is the aim of The Website Redesign?"],
    n_results=1
)

neo4j_client = GraphDatabase.driver(
  uri=os.getenv("NEO4J_URI"),
  auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

session = neo4j_client.session(database=os.getenv("NEO4J_DATABASE"))

query = """
MATCH (p:Project {name: "AI Chatbot"})<-[:WORKS_ON]-(person)
RETURN person.name, person.role;
"""

neo4j_result = session.run(query).data()
print(neo4j_result)

llm = ChatOpenAI(model_name=os.getenv("OPENAI_MODEL"))

template = """
Use the following context:
Neo4j Data: {structured_data}
ChromaDB Data: {unstructured_data}
Answer the user's question: {query}.
"""

prompt = PromptTemplate(
    input_variables=["structured_data", "unstructured_data", "query"],
    template=template
)

chain = prompt | llm
# user_query = 'Who manages the AI Chatbot?'
user_query = 'What is the focus of the AI Chatbot project and who works there?'
response = chain.invoke({
    "structured_data": neo4j_result,
    "unstructured_data": chromadb_result,
    "query": user_query
})
print(response)
