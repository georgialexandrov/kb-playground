import os
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from neo4j import GraphDatabase
import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings

llm = ChatOpenAI(model_name=os.getenv("OPENAI_MODEL"), temperature=0.0)

neo4j_client = GraphDatabase.driver(
  uri=os.getenv("NEO4J_URI"),
  auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)
session = neo4j_client.session(database=os.getenv("NEO4J_DATABASE"))

chroma_client = chromadb.HttpClient(
    host=os.getenv("CHROMADB_HOST"),
    port=os.getenv("CHROMADB_PORT"),
    ssl=False,
    headers=None,
    settings=Settings(),
    tenant=DEFAULT_TENANT,
    database=DEFAULT_DATABASE,
)

collection = chroma_client.get_collection("project_knowledge")

def get_schema():
  query = "CALL db.schema.visualization()"
  return session.run(query).data()

@tool
def enrich_structured_data(user_query):
  """
  Returns relevant information from the Neo4j database about the user query.
  """
  print("enrich_structured_data" + user_query)
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

  neo4j_response = neo4j_chain.invoke({
      "schema": get_schema(),
      "query": user_query
  })
  print(neo4j_response.content)
  neo4j_result = session.run(neo4j_response.content).data()
  print(neo4j_result)
  return neo4j_result

@tool
def enrich_unstructured_data(user_query):
  """
    Generate a query for the chromadb.
  """
  print("enrich_unstructured_data" + user_query)
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

  chromadb_result = collection.query(
    query_texts=[chroma_query_text],
    n_results=1
  )

  return chromadb_result
