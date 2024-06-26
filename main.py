import streamlit as st
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
from dotenv import load_dotenv
import os


# Load the .env file
load_dotenv()
# Page configuration

st.set_page_config(
    page_title="Island Chatbot",
    page_icon="🏝️",
)
# Navigation Bar
nav_option = st.sidebar.radio("Navigation", ("Model Viewer", "Chat", "AI"))
# container
header = st.container()
input = st.container()
viewer = st.container()
report = st.container()
graphs = st.container()


with header:
    st.title('Island Chatbot')
    st.info('Hi I am ..... and I am developed by team Island to extract and interact with the data from the revit model.')


# Input
with input:
    st.subheader('Inputs')

    # columns for input
    serverCol, tokenCol = st.columns([1, 3])
    speckleServer = serverCol.text_input('Speckle Server', 'https://speckle.xyz')
    speckleToken = tokenCol.text_input('Speckle Token', os.getenv('SPECKLE_TOKEN'))

    # client
    client = SpeckleClient(host=speckleServer)
    # get account from token
    account = get_account_from_token(speckleToken, speckleServer)
    # authenciaction
    client.authenticate_with_account(account)
    # streams list
    streams = client.stream.list()
    # st.write(streams)
    # get streams names
    streamNames = [s.name for s in streams]
    # dropdown for stream selection
    sName = st.selectbox('Select Stream', options=streamNames)
    # selected stream only
    stream = client.stream.search(sName)[0]
    # stream branches
    branches = client.branch.list(stream.id)
    branchNames = [b.name for b in branches]

    # Check if the stream has multiple branches
    if len(branchNames) > 1:
        bName = st.selectbox('Select Branch', options=branchNames)
    else:
        bName = branchNames[0] if branchNames else None

    # stream commits
    commits = client.commit.list(stream.id, limit=100)

# Definations
def commit2viewer(stream, commit, branch_name=None):
    if branch_name:
        embed_src = "https://speckle.xyz/embed?stream=" + stream.id + "&commit=" + commit.id + "&branch=" + branch_name
    else:
        embed_src = "https://speckle.xyz/embed?stream=" + stream.id + "&commit=" + commit.id
    print("Embed URL:", embed_src)  # Debugging statement
    return st.components.v1.iframe(src=embed_src, height=400, width=600)

with viewer:
    st.subheader('Viewer')
    if commits:
        selected_commit = None
        for commit in commits:
            if getattr(commit, "branchName", None) == bName:
                selected_commit = commit
                break
        if selected_commit:
            # Generate URL for the Speckle viewer
            embed_src = f"https://speckle.xyz/embed?stream={stream.id}&commit={selected_commit.id}"

            # Display the viewer in an iframe
            st.components.v1.iframe(src=embed_src, height=600, width=800)
        else:
            st.write("No commits available for the selected branch.")
    else:
        st.write("No commits available for the selected stream.")

# # Report
with report:
    st.subheader('Report')
    # Display some information about the selected stream and branch
    st.write(f"Selected Stream: {stream.name}")
    if branchNames:
        st.write(f"Selected Branch: {bName}")
    # Add more reporting functionalities as needed


# Footer
st.markdown(
    """
    ---
    Made with ❤️ by Island Team developed by [Ashish](https://ashu-a.github.io/ashish_ranjan/)
    """
)
