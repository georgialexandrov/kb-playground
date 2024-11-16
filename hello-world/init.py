import os
import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
from neo4j import GraphDatabase
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
collection = chroma_client.create_collection("project_knowledge")

collection.add(
  documents=[
      "The AI Chatbot project focuses on building a conversational agent with NLP capabilities.",
      "The Website Redesign project aims to overhaul the UI/UX of the company website."
  ],
  metadatas=[
      {"project": "AI Chatbot", "type": "description"},
      {"project": "Website Redesign", "type": "description"}
  ],
  ids=["doc1", "doc2"]
)

chromadb_result = collection.query(
    query_texts=["What is the AI Chatbot project about?"],
    # query_texts=["What is the aim of The Website Redesign?"],
    n_results=1
)

print(chromadb_result)

neo4j_client = GraphDatabase.driver(
  uri=os.getenv("NEO4J_URI"),
  auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

session = neo4j_client.session(database=os.getenv("NEO4J_DATABASE"))


queries = [
    "CREATE (:Person {name: 'Alice Smith', role: 'Developer', department: 'Engineering'})",
    "CREATE (:Person {name: 'Bob Jones', role: 'Project Manager', department: 'Engineering'})",
    "CREATE (:Person {name: 'Carol Lee', role: 'Designer', department: 'Product Design'})",
    "CREATE (:Project {name: 'AI Chatbot', description: 'Building an intelligent bot', start_date: '2024-01-01', end_date: '2024-12-31'})",
    "CREATE (:Project {name: 'Website Redesign', description: 'Overhauling the company site', start_date: '2024-03-01', end_date: '2024-09-30'})",
    "CREATE (:Department {name: 'Engineering', manager: 'Bob Jones'})",
    "CREATE (:Department {name: 'Product Design', manager: 'Carol Lee'})",
    "CREATE (:Document {title: 'Chatbot Roadmap', type: 'Plan', author: 'Bob Jones'})",
    "CREATE (:Document {title: 'UX Guidelines', type: 'Policy', author: 'Carol Lee'})",
    "MATCH (a:Person {name: 'Alice Smith'}), (d:Department {name: 'Engineering'}) CREATE (a)-[:WORKS_IN]->(d)",
    "MATCH (b:Person {name: 'Bob Jones'}), (d:Department {name: 'Engineering'}) CREATE (b)-[:MANAGES]->(d)",
    "MATCH (a:Person {name: 'Alice Smith'}), (p:Project {name: 'AI Chatbot'}) CREATE (a)-[:WORKS_ON]->(p)",
    "MATCH (p:Project {name: 'AI Chatbot'}), (doc:Document {title: 'Chatbot Roadmap'}) CREATE (p)-[:REFERENCES]->(doc)"
]

for query in queries:
    session.run(query)
