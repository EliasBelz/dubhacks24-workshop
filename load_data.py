import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from dotenv import load_dotenv
import pandas as pd

FILE_PATH = "data/cse_classes.csv"

print(f"Uploading {FILE_PATH} to ChromaDB")

load_dotenv()

google_ef  = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=os.environ["API_KEY"])
client = chromadb.PersistentClient(path="./data/vectorDB")

# comment out the following line if you have already created the collection
collection = client.create_collection(
    name="my_collection",
    embedding_function=google_ef,
    metadata={"hnsw:space": "cosine"}
)

# uncomment the following line if you have already created the collection
# collection = client.get_collection(name="my_collection", embedding_function=google_ef)

# Replace with the path to your CSV file
df = pd.read_csv(FILE_PATH)

documents = []
ids = []

for index, row in df.iterrows():
    ids.append(f"{FILE_PATH}{index + 1}")
    formatted_row = ''.join([f"'{col}: {row[col]}'\n" for col in df.columns])
    documents.append(formatted_row)

print("CSV indexed, uploading to ChromaDB...")
print("This may take a minute...")

collection.add(documents=documents,ids=ids)
print("Upload complete!")
print(f"{collection.count()} documents in collection.")
