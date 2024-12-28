## This file will contain the code realted with App's UI. It will need to deployed as application
### on EC2. Another option is to dockerize it and deploy it on ECS
import json

import streamlit as st
import requests

bucket_name = 'capleasemanager'
ip_address = '18.117.158.226'


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
            history = []
            query_params = {"query": user_question, "history": history}
            response = requests.post(f"http://{ip_address}:8000/getLeaseInfo", params=query_params)
            if response.status_code == 200:
                response_data = response.json()
                response_data = json.loads(response_data)
                for key in response_data:
                    response_value = json.loads(response_data[key])
                    st.success(response_value["answer"])
            else:
                st.error(response.content)



if __name__ == "__main__":
    main()
