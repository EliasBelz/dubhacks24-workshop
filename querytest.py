import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from dotenv import load_dotenv

load_dotenv()

google_ef  = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=os.environ["API_KEY"])
client = chromadb.PersistentClient(path="./data/vectorDB")
collection = client.get_collection(name="my_collection", embedding_function=google_ef)


results = collection.query(
    query_texts=["Web programming"], # Chroma will embed this for you
    n_results=3 # how many results to return
)

for c in results["documents"][0]:
  print(c)