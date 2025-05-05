from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

groq_api_key="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"
os.environ["GOOGLE_API_KEY"]= "AIzaSyC87rM9xeEqJ6Rt5LhguLed6QK5mzT6XBM"

llm=ChatGroq(groq_api_key=groq_api_key,
             model_name="mixtral-8x7b-32768")

def vector_embedding(file_path, name):

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    loader = TextLoader(file_path, encoding='utf-8')
    docs=loader.load()
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200) ## Chunk Creation
    final_documents=text_splitter.split_documents(docs[:20]) #splitting
    vectors=FAISS.from_documents(final_documents,embeddings) #vector google embeddings
    index_path = "faiss_index" + name
    vectors.save_local("faiss_index",name)
    return vectors

vectors = vector_embedding(r"files\YTUMap.txt","YTUMap")
