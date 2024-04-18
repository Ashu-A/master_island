import streamlit as st
import pandas as pd
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
from specklepy.api import operations

# Load the .env file if needed
# from dotenv import load_dotenv
# load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Island Chatbot",
    page_icon="🏝️",
)

# Input section
st.subheader('Inputs')

speckleServer = st.text_input('Speckle Server', 'https://speckle.xyz')
speckleToken = st.text_input('Speckle Token', 'YOUR_ACCESS_TOKEN')

# Initialize Speckle client with server URL
client = SpeckleClient(host=speckleServer)

# Authenticate the client with the access token
client.authenticate_with_token(speckleToken)

# Streams list
try:
    streams = client.stream.list()
    streamNames = [s.name for s in streams]
    sName = st.selectbox('Select Stream', options=streamNames)
    # Check if a stream is selected
    if sName:
        stream = client.stream.search(sName)[0]
    else:
        st.error("No stream selected.")
        stream = None
except Exception as e:
    # Handle any errors that occur during stream retrieval
    st.error(f"An error occurred while retrieving streams: {e}")
    stream = None

# Stream branches
branches = client.branch.list(stream.id)
branchNames = [b.name for b in branches]

if len(branchNames) > 1:
    bName = st.selectbox('Select Branch', options=branchNames)
else:
    bName = branchNames[0] if branchNames else None

# Stream commits
commits = client.commit.list(stream.id, limit=100)

# Commit URL
commit_url = st.text_input('Commit URL', "https://speckle.xyz/streams/06564bda95/commits/f308ed526e")

# Get commit data
commit_data = None

# Try to get the commit data
try:
    commit = client.commit.get(stream_id=stream.id, commit_id=commit_url.split('/')[-1])
    obj_id = commit.referencedObject
    transport = client.transport
    commit_data = operations.receive(obj_id, transport)
except Exception as e:
    # Handle any errors that occur during commit retrieval
    st.error(f"An error occurred while retrieving commit data: {e}")

# Data section
if commit_data:
    st.subheader("Data")
    # Display data extracted from the selected commit
    # You need to modify this part based on your specific data structure
    st.write(commit_data)
else:
    st.write("No commit data available.")

# Footer
st.markdown(
    """
    ---
    Made with ❤️ by Island Team developed by [Ashish](https://ashu-a.github.io/ashish_ranjan/)
    """
)
