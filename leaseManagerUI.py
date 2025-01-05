## This file will contain the code realted with App's UI. It will need to deployed as application
### on EC2. Another option is to dockerize it and deploy it on ECS
import json
from collections import deque

import streamlit as st
import requests

bucket_name = 'capleasemanager'
ip_address = 'ec2-3-145-41-180.us-east-2.compute.amazonaws.com'


def fetch_lease_info_response(url, user_query):
    # Check if the URL is already in the cache
    history = []
    for cached_url, cached_response in st.session_state.api_cache:
        if cached_url == url:
            # st.write("Fetched from cache!")
            history.append({
                'role': cached_response[0],
                'content': str(cached_response[1])
            })
    payload = {"query": user_query, "history": history}
    # If not cached, make an API call
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        # Add the response to the cache
        st.session_state.api_cache.append((url, ('user', payload['query'])))
        response_data = response.json()
        response_data = response_data['response']

        response_data = json.loads(response_data)
        for key in response_data:
            response_value = json.loads(response_data[key])
            st.session_state.api_cache.append((url, ('assistant', response_value["answer"])))
            st.success(response_value["answer"])

    else:
        st.error(response.content)


##Only for local testing. We will using lambda to invoke the LLM via Bedrock
def main():
    st.set_page_config("Lease Manager")

    st.header("Lease Manager")

    user_question = st.text_input("Ask a Question Related With Leases")

    with st.sidebar:
        st.title("Add More Leases and update system:")
        uploaded_files = st.file_uploader("Choose lease pages to upload", type=["png", "jpeg"],
                                         accept_multiple_files=True)
        print("uploaded_files:  ",uploaded_files)
        if st.button("Upload Lease Data"):
            with st.spinner("Processing..."):
                files = [
                    ("files", (file.name, file, file.type)) for file in uploaded_files
                ]
                upload_file_response = requests.post(f"http://{ip_address}:8000/uploadFilesToS3/", files=files)
                st.write(upload_file_response.status_code)
                st.write(upload_file_response.content)
                if upload_file_response.status_code == 200:
                    st.success(upload_file_response.content)
                else:
                    st.error(upload_file_response.content)
        if st.button("Generate Vectors"):
            with st.spinner("Processing..."):
                generate_vector_response = requests.post(f"http://{ip_address}:8000/generate-vectors")
                if generate_vector_response.status_code == 200:
                    st.success(generate_vector_response.content)
                else:
                    st.error(generate_vector_response.content)

    if st.button("Output"):
        with st.spinner("Processing..."):
            # @TODO Add code to (1) invoke the getLeaseInfo API via APIGateway
            url = f"http://{ip_address}:8000/getLeaseInfo"
            fetch_lease_info_response(url, user_question)
    if st.button("Clear Cache"):
        st.session_state.api_cache.clear()
        st.success("Cache cleared successfully!")



if __name__ == "__main__":
    if "api_cache" not in st.session_state:
        st.session_state.api_cache = deque(maxlen=6)
    main()
