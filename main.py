import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional
from fastapi import FastAPI, HTTPException


# --- Import RAG Components ---
# Adjust imports based on your specific libraries and document types
from langchain_community.document_loaders import PyPDFLoader, TextLoader # Example loaders
from langchain.text_splitter import RecursiveCharacterTextSplitter
# --- Use Google-specific imports ---
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma # Still using ChromaDB local vector store
from langchain.chains import RetrievalQA


# --- Configuration ---
# Load environment variables from .env file
load_dotenv()

# Get Google API key from environment variable
# --- Correct variable name for Google API key ---
LLM_API_KEY = os.getenv("GOOGLE_API_KEY")
if not LLM_API_KEY:
     print("Error: GOOGLE_API_KEY not found in environment variables. Please set it in the .env file.")
     # For local testing, you might print a message.
     # In a production system, you'd likely want this check to prevent startup errors
     # or handle missing keys more robustly.
     # Example: raise ValueError("GOOGLE_API_KEY not found")


document_directory = "./docs"
persist_directory = "./chroma_db" # Directory to store the ChromaDB persistent data

# --- Initialize FastAPI App ---
app = FastAPI(
    title="Document RAG Q&A API (Google Gemini)",
    description="API for asking questions about documents using RAG with Google Gemini.",
    version="1.0.0",
)

# --- Global Variables for RAG Components ---
vectorstore: Optional[Chroma] = None
retrieval_qa_chain: Optional[RetrievalQA] = None
embeddings_model: Optional[GoogleGenerativeAIEmbeddings] = None
llm_model: Optional[ChatGoogleGenerativeAI] = None

# --- Startup Event: Initialize RAG Components ---
@app.on_event("startup")
async def startup_event():
    print("FastAPI app startup: Initializing RAG components with Google Gemini...")
    global vectorstore, retrieval_qa_chain, embeddings_model, llm_model

    # Ensure API key is available before proceeding
    if not LLM_API_KEY:
         print("API key missing. Skipping RAG initialization. API endpoints will not work.")
         return # Exit startup if key is missing

    try:
        # --- RAG Setup Logic (Adapted for Google Models) ---

        # Initialize the embedding model
        # --- Use Google's Embedding Model ---
        # 'models/embedding-001' is a common embedding model name for Google GenAI
        embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=LLM_API_KEY)
        print("Google Embedding model initialized ('models/embedding-001').")

        # Check if vector store already exists or needs creation
        if os.path.exists(persist_directory) and os.listdir(persist_directory):
            print(f"Loading existing vector store from {persist_directory}...")
            # Load ChromaDB with the correct embedding function
            vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings_model)
            print("Vector store loaded from disk.")
        else:
            print(f"Vector store not found at {persist_directory}. Starting document ingestion...")
            documents = []
            if os.path.exists(document_directory):
                for file in os.listdir(document_directory):
                    file_path = os.path.join(document_directory, file)
                    if os.path.isfile(file_path):
                        try:
                            if file.endswith(".pdf"):
                                loader = PyPDFLoader(file_path)
                                documents.extend(loader.load())
                            elif file.endswith(".txt"):
                                loader = TextLoader(file_path)
                                documents.extend(loader.load())
                            # Add more loaders here if needed
                            # print(f"Loaded {file}") # Uncomment for verbose loading
                        except Exception as e:
                            print(f"Error loading {file}: {e}")

            if not documents:
                print(f"No documents loaded from {document_directory}. Vector store will be empty.")
                vectorstore = None
            else:
                print(f"Successfully loaded {len(documents)} document pages/parts.")
                # Split Documents
                print("Splitting documents into chunks...")
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000, # Experiment
                    chunk_overlap=200 # Experiment
                )
                chunked_documents = text_splitter.split_documents(documents)
                print(f"Split into {len(chunked_documents)} chunks.")

                # Create Embeddings and Index
                print("Creating embeddings and indexing chunks in ChromaDB...")
                # --- Create ChromaDB from chunks with Google Embeddings ---
                vectorstore = Chroma.from_documents(
                    chunked_documents,
                    embeddings_model,
                    persist_directory=persist_directory
                )
                print("Indexing complete. Vector store saved.")


        # --- Initialize the LLM and QA Chain ---
        # Initialize the LLM model
        if LLM_API_KEY: # Only initialize LLM if API key is present
             # --- Use Google's Chat Model ---
             # 'gemini-pro' is a common chat model name for Google GenAI
             llm_model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.1, google_api_key=LLM_API_KEY)
             print("Google LLM model initialized ('gemini-pro').")

             # Create a retriever from the vector store if it was initialized
             if vectorstore:
                 retriever = vectorstore.as_retriever(search_kwargs={"k": 3}) # Retrieve top 3
                 # Create the RAG chain
                 retrieval_qa_chain = RetrievalQA.from_chain_type(
                     llm_model,
                     chain_type="stuff",
                     retriever=retriever,
                     return_source_documents=True # Optional
                 )
                 print("Retrieval QA chain initialized.")
             else:
                 print("Vector store is empty or failed to initialize. Retrieval QA chain not fully set up.")
                 retrieval_qa_chain = None # Explicitly set to None

        else:
             print("API key missing, LLM and QA chain not initialized.")


    except Exception as e:
        print(f"FATAL ERROR during RAG component initialization: {e}")
        # In a production app, this would likely require immediate attention
        vectorstore = None
        retrieval_qa_chain = None
        embeddings_model = None
        llm_model = None
        # Consider if the app should exit or run in a degraded state

# --- Define Request Body Schema (Same as before) ---
class QueryRequest(BaseModel):
    query: str

# --- Define Response Body Schema (Optional - Same as before) ---
# class AnswerResponse(BaseModel):
#     answer: str
#     # source_documents: Optional[list] = None


# --- Define API Endpoint (Same logic, just awaits async call) ---
@app.post("/ask")
async def ask_document(request: QueryRequest):
    """
    Receives a question and returns an answer based on the document corpus using RAG with Google Gemini.
    """
    print(f"Received query: {request.query}")

    # Check if RAG components were initialized successfully
    # Also check if the chain is actually set up (requires vectorstore and LLM)
    if retrieval_qa_chain is None:
        print("RAG chain not initialized. Returning error.")
        raise HTTPException(status_code=500, detail="RAG system is not ready or initialized. Check server logs.")

    try:
        # Call the RAG chain asynchronously
        # --- Use ainvoke for async call with LangChain chains ---
        response = await retrieval_qa_chain.ainvoke({"query": request.query})

        # Extract the answer
        answer = response.get("result", "Could not retrieve an answer.")

        # Optional: Extract sources
        # sources = response.get("source_documents", [])
        # formatted_sources = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in sources]

        print("Query processed successfully.")
        # Return the answer in a JSON response
        # return AnswerResponse(answer=answer)#, source_documents=formatted_sources)
        return {"answer": answer} # Simple dictionary response

    except Exception as e:
        print(f"Error processing query: {e}")
        # Return an HTTP exception
        raise HTTPException(status_code=500, detail=f"An error occurred while processing your query: {e}")

# --- Optional: Root Endpoint (Same as before) ---
@app.get("/")
async def read_root():
    return {"message": "Document RAG Q&A API (Google Gemini) is running. Go to /docs for documentation."}
