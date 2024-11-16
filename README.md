# Knowledge Graph Playground

## Prerequisites

Make sure you have Docker installed on your machine.

## Running the Environment

To start the environment, run the following command:

```sh
docker-compose up
```

This command will start four containers:

- [OpenWebUI](https://openwebui.com) is accessible at [http://localhost:8080](http://localhost:8080). Sign up to create a new user.
- [Neo4j](https://neo4j.com) is accessible at [http://localhost:7474](http://localhost:7474). The password is `testtest`.
- [ChromaDB](https://cookbook.chromadb.dev) is accessible at [http://localhost:8000](http://localhost:8000).
- [Chroma Admin](https://chromadb-admin.com) is accessible at [http://localhost:3030](http://localhost:3030). To connect, enter `http://kg-playground-chroma:8000` as the host.

## Setting Up the Hello World Example

To set up the hello world example, create a `.env` file in the root directory. Ensure the content matches the `.env.example` file and includes your OpenAI and LangSmith API keys. If you do not wish to use LangSmith, you can remove the LANGSMITH keys from the `.env` file.