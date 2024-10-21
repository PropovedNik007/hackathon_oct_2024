import csv
import hashlib
import os
import pandas as pd
import pickle
import PyPDF2
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings.base import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from numpy import dot
from numpy.linalg import norm

# Load OpenAI key
if not load_dotenv():
    raise Exception('Error loading .env file. Make sure to place a valid OPEN_AI_KEY in the .env file.')

REPORTS_SAVE_PATH = 'data/sample_reports'
LABELED_EXAMPLES_PATH = 'data/labels/greenwashing.csv'  # Path to your labeled CSV file
DB_PATH = "data/db/sample.db"
LABELED_DB_PATH = "data/db/labeled.db"
MODEL = "gpt-4o"

# 1. Load ESG Reports (PDFs)
def get_documents_from_path(files_path: str) -> [Document]:
    documents = []
    for file in os.listdir(files_path):
        _, file_extension = os.path.splitext(file)
        text = ""
        if file_extension == ".pdf":
            try:
                with open(os.path.join(files_path, file), 'rb') as f:
                    reader = PyPDF2.PdfReader(f, strict=False)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e:
                print(f"ERROR: {e}")
            if text:
                documents.append(Document(page_content=text, metadata={"source": file}))
            else:
                print(f"WARNING: No text extracted from {file}")
        else:
            raise Exception(f"Unsupported file extension: {file_extension}")
    return documents

# 2. Load labeled greenwashing examples from CSV
def get_labeled_examples_from_csv(file_path: str) -> [Document]:
    labeled_examples = []
    df = pd.read_csv(file_path, sep=';')

    for index, row in df.iterrows():
        text = row['text']
        label = row['greenwashing']
        category = row['type']

        if pd.isna(text):
            print(f"WARNING: Missing text at row {index}, skipping this entry.")
            continue

        # Create a document with metadata
        labeled_examples.append(Document(page_content=text, metadata={"label": label, "category": category}))

    return labeled_examples

# 3. Create the vector databases
def create_db(documents=False, labeled_documents=True):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=100, separators=["\n\n", "\n"])
    embeddings = OpenAIEmbeddings()

    # Load and create a vector database for ESG reports
    if documents:
        documents = get_documents_from_path(REPORTS_SAVE_PATH)
        texts = text_splitter.split_documents(documents)
        db = FAISS.from_documents(texts, embeddings)
        with open(DB_PATH, "wb") as f:
            pickle.dump(db.serialize_to_bytes(), f)
    
    # Load and create a vector database for labeled greenwashing examples
    if labeled_documents:
        labeled_documents = get_labeled_examples_from_csv(LABELED_EXAMPLES_PATH)
        labeled_texts = text_splitter.split_documents(labeled_documents)
        labeled_db = FAISS.from_documents(labeled_texts, embeddings)
        with open(LABELED_DB_PATH, "wb") as f:
            pickle.dump(labeled_db.serialize_to_bytes(), f)

# 4. Cosine similarity function for embeddings
def cosine_similarity(a, b):
    return dot(a, b) / (norm(a) * norm(b))

# 5. Check if a chunk is relevant before sending to OpenAI
def is_relevant_chunk(chunk, embeddings, labeled_db, SIMILARITY_THRESHOLD=0.8):
    chunk_embedding = embeddings.embed_query(chunk)
    similar_docs = labeled_db.similarity_search_by_vector(chunk_embedding, k=1)
    
    if similar_docs:
        most_similar_doc = similar_docs[0]
        most_similar_embedding = embeddings.embed_query(most_similar_doc.page_content)
        similarity_score = cosine_similarity(chunk_embedding, most_similar_embedding)
        return similarity_score >= SIMILARITY_THRESHOLD
    return False

# 6. Label greenwashing using OpenAI (only for relevant chunks)
def label_greenwashing(query_chunk, seen_chunks, embeddings, labeled_db, retrieval_chain_greenwashing):
    # chunk_hash = hashlib.md5(query_chunk.encode('utf-8')).hexdigest()
    # chunk_text = query_chunk.replace('\n', ' ').strip()
    chunk_text = query_chunk.replace('\n', ' ').replace('\u2003', ' ').replace('\xa0', ' ').strip()
    
    if chunk_text in seen_chunks:
        return []  # Skip duplicate chunks
    seen_chunks.add(chunk_text)

    if is_relevant_chunk(chunk_text, embeddings, labeled_db):
        # If the chunk is relevant, call OpenAI to label greenwashing
        greenwashing_response = retrieval_chain_greenwashing({"query": chunk_text})
        labels = []

        best_match = None
        best_similarity = 0

        for document in greenwashing_response['source_documents']:
            # Calculate similarity between the query chunk and the retrieved document
            doc_embedding = embeddings.embed_query(document.page_content.strip())
            query_embedding = embeddings.embed_query(chunk_text)
            similarity = cosine_similarity(query_embedding, doc_embedding)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = document
        
        if best_match:
            label_data = {
                "report_chunk": chunk_text,  # Use cleaned chunk without \n and other unwanted characters
                "category": best_match.metadata['category'] if 'category' in best_match.metadata else 'Uncategorized',
                "retrieved_quote": best_match.page_content.strip(),
                "retrieved_similarity": best_similarity,
            }
            labels.append(label_data)
            print(f"Best greenwashing match detected: {label_data}")
        
        return labels
    return []  # Skip chunks not deemed relevant

# 7. Analyze ESG reports for greenwashing
def analyze_report_for_greenwashing(documents, embeddings, labeled_db, retrieval_chain_greenwashing):
    seen_chunks = set()  # Track already processed chunks to avoid duplicates
    report_analysis = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=100)  # Split the document into chunks

    for doc in documents:
        chunks = text_splitter.split_text(doc.page_content)  # Split the document into smaller chunks
        for chunk in chunks:
            labels = label_greenwashing(chunk, seen_chunks, embeddings, labeled_db, retrieval_chain_greenwashing)
            report_analysis.extend(labels)  # Collect all labels into a single list
    return report_analysis

# 8. Save collected labels to CSV
def save_labels_to_csv(labels, csv_filename="greenwashing_analysis.csv"):
    if not labels:
        print("No relevant greenwashing labels found.")
        return
    keys = labels[0].keys()  # Get the keys from the first dictionary for the CSV header
    with open(csv_filename, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(labels)

# 9. Extract and analyze document
def extract_document(file_path: str) -> [Document]:
    documents = []
    _, file_extension = os.path.splitext(file_path)
    text = ""
    
    if file_extension == ".pdf":
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f, strict=False)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"ERROR: {e}")
            
        if text:
            documents.append(Document(page_content=text, metadata={"source": file_path}))
        else:
            print(f"WARNING: No text extracted from {file_path}")
    return documents

# 10. Main RAG system to detect greenwashing
def rag():
    # Load the vector database for labeled greenwashing examples
    with open(LABELED_DB_PATH, "rb") as f:
        labeled_db_bytes = pickle.load(f)
        labeled_db = FAISS.deserialize_from_bytes(labeled_db_bytes, OpenAIEmbeddings(), allow_dangerous_deserialization=True)

    # Load the LLM
    llm = ChatOpenAI(model_name=MODEL, temperature=0)  # For deterministic outputs
    embeddings = OpenAIEmbeddings()  # For embedding generation

    # Retrieval chains for greenwashing detection
    retrieval_chain_greenwashing = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=labeled_db.as_retriever(),
        return_source_documents=True,
    )

    # Load and analyze ESG report
    document_path = "Apple_Environmental_Progress_Report_2021.pdf"
    documents = extract_document(f"data/sample_reports/{document_path}")
    report_labels = analyze_report_for_greenwashing(documents, embeddings, labeled_db, retrieval_chain_greenwashing)
    
    # Save the labels to a CSV
    save_labels_to_csv(report_labels, f"./data/sample_labels/{document_path}.csv")
    return report_labels




if __name__ == "__main__":
    # create_db(documents=False, labeled_documents=True)
    # Uncomment to create the databases (run once)
    create_db(documents=False, labeled_documents=True)

    # Run the RAG system to detect greenwashing
    output_labels = rag()