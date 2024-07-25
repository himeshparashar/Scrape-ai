import streamlit as st
import requests
import json

# Set up the FastAPI endpoints
BASE_URL = "https://nsdc.ayecampaigns.com"  # Replace with your FastAPI server URL

# Function to test the web scraper API
def test_web_scraper(urls, collection_name, collection_id, user_id):
    endpoint = f"{BASE_URL}/v1/knowledgebase/urls"
    data = {
        "urls": urls,
        "collection_name": collection_name,
        "collection_id": collection_id,
        "user_id": user_id,   }
    response = requests.post(endpoint, json=data)
    return response.json()

# Function to test the email template API
def test_email_template(prompt, collection_name, max_token):
    endpoint = f"{BASE_URL}/v1/data_retriever/data_retriever"
    data = {
        "collection_name": collection_name,
        "prompt": prompt,
        "max_token": max_token,
    }
    response = requests.post(endpoint, json=data)
    return response.json()

# Streamlit UI
st.title("FastAPI Testing with Streamlit")

st.header("Web Scraper API")
urls = st.text_input("URLs (comma-separated)")
collection_name = st.text_input("Collection Name")
collection_id = st.text_input("Collection ID")
user_id = st.text_input("User ID")

if st.button("Test Web Scraper API"):
    if urls and collection_name and collection_id and user_id:
        result = test_web_scraper(urls, collection_name, collection_id, user_id)
        st.json(result)
    else:
        st.error("Please fill in all required fields")

st.header("Retrival")
prompt = st.text_area("Prompt")
collection_name_et = st.text_input("Collection Name (Email Template)")
max_token = st.number_input("Max Token", min_value=1, value=500)

if st.button("Test Email Template API"):
    if prompt  and collection_name_et:
        result = test_email_template(prompt, collection_name_et, max_token,)
        st.json(result)
    else:
        st.error("Please fill in all required fields")

