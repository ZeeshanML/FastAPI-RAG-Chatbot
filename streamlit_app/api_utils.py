import requests
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")

def get_chat_response(question, session_id, model):
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    data = {"question" : question, "model" : model}
    if session_id:
        data["session_id"] = session_id

    try:
        response = requests.post(f"{API_BASE_URL}/chat", headers = headers, json = data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API request failed with status code {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None
    
def upload_document(file):
    try:
        files = {"file" : (file.name, file, file.type)}
        response = requests.post(f"{API_BASE_URL}/upload-doc", files = files)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to upload file. Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred while uploading the file: {str(e)}")
        return None
    
def list_documents():
    try:
        response = requests.get(f"{API_BASE_URL}/list-docs")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to list documents. Error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"An error occurred while listing documents: {str(e)}")
        return []
    
def delete_document(file_id):
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    data = {"file_id": file_id}

    try:
        response = requests.post(f"{API_BASE_URL}/delete-doc", headers = headers, json = data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to delete document. Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred while deleting the document: {str(e)}")
        return None