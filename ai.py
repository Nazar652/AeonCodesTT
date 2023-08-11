import os
import uuid

from langchain import OpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA

from config import api_key


class QA:
    def __init__(self, path):
        os.environ['OPENAI_API_KEY'] = api_key
        loader = PyPDFLoader(path)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)

        persist_directory = f"./storage/{str(uuid.uuid4())}"
        embeddings = OpenAIEmbeddings()
        vectordb = Chroma.from_documents(documents=texts,
                                         embedding=embeddings,
                                         persist_directory=persist_directory)
        vectordb.persist()

        retriever = vectordb.as_retriever()
        llm = OpenAI()
        self.qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    def get_response(self, user_input):
        query = f"###Prompt {user_input}"
        try:
            llm_response = self.qa(query)
            return llm_response
        except Exception as err:
            return {'result': f"An error has occurred. \n{str(err)}"}
