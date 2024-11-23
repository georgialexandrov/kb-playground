import os
import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
from neo4j import GraphDatabase
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
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

neo4j_client = GraphDatabase.driver(
  uri=os.getenv("NEO4J_URI"),
  auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

session = neo4j_client.session(database=os.getenv("NEO4J_DATABASE"))

def get_schema():
  query = "CALL db.schema.visualization()"
  result = session.run(query).data()
  return result

schema = get_schema()
print(schema)

llm = ChatOpenAI(model_name=os.getenv("OPENAI_MODEL"), temperature=0.0)

template = """
Based on the following Neo4j schema, generate a Cypher query to retrieve structured data relevant to the user's question:
Neo4j schema: {schema}
User question: {query}

The response must be a valid Cypher query that can be executed directly in a Neo4j database. Do not include any additional information, formatting, or markdown. Only return the Cypher query.
"""

neo4j_prompt = PromptTemplate(
    input_variables=["schema", "query"],
    template=template
)

neo4j_chain = neo4j_prompt | llm
user_query = 'Who manages the AI Chatbot?'
# user_query = 'What is the focus of the AI Chatbot project and who works there?'
neo4j_response = neo4j_chain.invoke({
    "schema": schema,
    "query": user_query
})
print(neo4j_response.content)

neo4j_result = session.run(neo4j_response.content).data()

chroma_prompt_template = """
Based on the user's question, generate a query to retrieve relevant unstructured data from ChromaDB:
User question: {query}

The response must be a valid query text that can be used to query ChromaDB. Do not include any additional information, formatting, or markdown. Only return the query text.
"""

chroma_prompt = PromptTemplate(
  input_variables=["query"],
  template=chroma_prompt_template
)

chroma_chain = chroma_prompt | llm
chroma_query_response = chroma_chain.invoke({
  "query": user_query
})

chroma_query_text = chroma_query_response.content.strip()

print(chroma_query_text)
chromadb_result = collection.query(
  query_texts=[chroma_query_text],
  n_results=1
)

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

# user_query = 'What is the focus of the AI Chatbot project and who works there?'
response = chain.invoke({
    "structured_data": neo4j_result,
    "unstructured_data": chromadb_result,
    "query": user_query
})
print(response)
