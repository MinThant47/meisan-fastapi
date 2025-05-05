from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.prompts import MessagesPlaceholder
from llm_and_route_query import llm
import os

os.environ["GOOGLE_API_KEY"]= "AIzaSyC87rM9xeEqJ6Rt5LhguLed6QK5mzT6XBM"

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

def load_FAISS_index(faiss_name):
    vectors = FAISS.load_local("faiss_index", embeddings, faiss_name, allow_dangerous_deserialization=True)
    return vectors

def get_context(index_path, question, sample_prompt, chat_history):
    vectors = load_FAISS_index(index_path)
    document_chain=create_stuff_documents_chain(llm,sample_prompt)
    retriever=vectors.as_retriever()

    retrieval_chain=create_retrieval_chain(retriever,document_chain)
    response=retrieval_chain.invoke({'input':question, "chat_history": chat_history})
    return response
