import json

import streamlit as st
import requests

# Set up the FastAPI endpoints
# BASE_URL = "https://nsdc.ayecampaigns.com"  # Replace with your FastAPI server URL
BASE_URL = "http://localhost:8008"  # Replace with your FastAPI server URL
# BASE_URL = "https://6cd8-2401-4900-1c8e-29b4-7846-30af-62c1-20bc.ngrok-free.app/"  # Replace with your FastAPI server URL

# Function to fetch collection names

def main():
    st.sidebar.title("API List")
    page = st.sidebar.radio("Go to", ["Chatbot_API", "Web_Scraper_API", "LoadData"])

    if page == "Web_Scraper_API":
        Web_Scraper_API()
    elif page == "Chatbot_API":
        Chatbot_API()
    elif page == "LoadData":
        LoadData()


def fetch_collection_names():
    endpoint = f"{BASE_URL}/v1/get_collection_list"
    response = requests.get(endpoint)
    if response.status_code == 200:
        raw_data = response.json()
        # Flatten the list structure and clean up the response to get collection names
        collection_names = [item[0] for item in raw_data if isinstance(item, list) and len(item) > 0]
        return collection_names
    else:
        return []

# Function to test the web scraper API
def test_web_scraper(urls, collection_name, collection_id, user_id):
    endpoint = f"{BASE_URL}/v1/knowledgebase/urls"
    data = {
        "urls": urls,
        "collection_name": collection_name,
        "collection_id": collection_id,
        "user_id": user_id,
    }
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

def load_txt_file(collection_name, collection_id, user_id, file_name):
    endpoint = f"{BASE_URL}/v1/knowledgebase/textloader"
    data = {
        "collection_name": collection_name,
        "collection_id": collection_id,
        "user_id": user_id,
        "file_name": file_name,
    }
    response = requests.post(endpoint, json=data)
    return response.json()

# Streamlit UI
st.title("NSDC Web Scraper")

# Fetch collection names for the dropdown
collection_names = fetch_collection_names()

def Web_Scraper_API():
    st.header("Web Scraper API")
    urls = st.text_input("URLs (comma-separated)")
    collection_name = st.text_input("Collection Name")
    collection_id = st.text_input("Collection ID")
    user_id = st.text_input("User ID")

    if st.button("Scrape URL"):
        if urls and collection_name and collection_id and user_id:
            result = test_web_scraper(urls, collection_name, collection_id, user_id)
            if result.get("status") == 200:
                data = result.get("data")
                st.write( data)
            else:
                st.error(result.get("message"))
        else:
            st.error("Please fill in all required fields")

def Chatbot_API():
    st.header("Chatbot API")
    prompt = st.text_area("Prompt")
    collection_name_et = st.selectbox("Collection Name (Email Template)", options=collection_names)
    max_token = st.number_input("Max Token", min_value=1, value=2000)

    if st.button("Send Request"):
        if prompt and collection_name_et:
            result = test_email_template(prompt, collection_name_et, max_token)
            if result.get("status") == 200:
                data = result.get("data")  # Extract only the "data" field
                # st.write(data)
                cleaned_string = data.strip('```json').strip('```').strip()
                data1 = json.loads(cleaned_string)
                if data1:
                    # Display the answer
                    st.header("Answer")
                    st.write(data1.get("answer", "No answer provided"))

                    # Display reference links if available
                    urls = data1.get("urls", [])
                    if urls:
                        st.header("Reference Links")

                        for i in range(0, len(urls), 2):
                            col1, col2 = st.columns(2)

                            with col1:
                                url = urls[i]
                                title = url.get("title", "Untitled")
                                nsdc_url = url.get("nsdc_url", "")
                                youtube_url = url.get("youtube_url", "")

                                if nsdc_url or youtube_url:
                                    st.subheader(title)
                                    if nsdc_url:
                                        st.markdown(f"[NSDC Link]({nsdc_url})")
                                    if youtube_url:
                                        st.video(youtube_url)

                            if i + 1 < len(urls):
                                with col2:
                                    url = urls[i + 1]
                                    title = url.get("title", "Untitled")
                                    nsdc_url = url.get("nsdc_url", "")
                                    youtube_url = url.get("youtube_url", "")

                                    if nsdc_url or youtube_url:
                                        st.subheader(title)
                                        if nsdc_url:
                                            st.markdown(f"[NSDC Link]({nsdc_url})")
                                        if youtube_url:
                                            st.video(youtube_url)

                # st.markdown(data,unsafe_allow_html=True)
            else: # If the status code is not 200
                st.error(result.get("message"))
        else:
            st.error("Please fill in all required fields")

def LoadData():
    st.header("Load Data")
    file_name = st.text_input("File Name")
    collection_name_ld = st.text_input("Collection Name (Load Data)")
    collection_id_ld = st.text_input("Collection ID (Load Data)")
    user_id_ld = st.text_input("User ID (Load Data)")

    if st.button("Load Data"):
        if file_name and collection_name_ld and collection_id_ld and user_id_ld:
            result = load_txt_file(collection_name_ld, collection_id_ld, user_id_ld, file_name)
            if result.get("status") == 200:
                data = result.get("data")
                st.write(data)
            else:
                st.error(result.get("message"))
        else:
            st.error("Please fill in all required fields")

# st.chat_input("Chat Input")
if __name__ == "__main__":
    main()