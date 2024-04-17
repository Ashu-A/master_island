import streamlit as st
import pandas as pd
from pandasai.llm.openai import OpenAI
import os
from specklepy.api.wrapper import StreamWrapper
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
import plotly.express as px
from dotenv import load_dotenv
from specklepy.api import operations
from pandasai import SmartDataframe


# Load the .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Island Chatbot",
    page_icon="🏝️",
)

def chat_speckle(df, prompt):
    openai_api_token = os.getenv('OPENAI_API_TOKEN')
    llm = OpenAI(api_token=openai_api_token)
    df = SmartDataframe(df, config={"llm": llm})
    result = df.chat(prompt)
    return result
def get_parameter_names(commit_data, selected_category):
    parameters = commit_data[selected_category][0]["parameters"].get_dynamic_member_names()
    parameters_names = []
    for parameter in parameters:
        parameters_names.append(commit_data[selected_category][0]["parameters"][parameter]["name"])
    parameters_names = sorted(parameters_names)
    return parameters_names

def get_parameter_by_name(element, parameter_name, dict):
    for parameter in parameters:
        key = element["parameters"][parameter]["name"]
        if key == parameter_name:
            dict[key] = element["parameters"][parameter]["value"]
    return dict


# container
header = st.container()
input = st.container()
viewer = st.container()
data = st.container()
report = st.container()
graphs = st.container()

# Header
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
    commit_url = st.text_input('Commit URL', "https://speckle.xyz/streams/06564bda95/commits/f308ed526e")

# wrapper
wrapper = StreamWrapper(commit_url)
# client
client = SpeckleClient(https://speckle.xyz) 
client.authenticate_with_token(ACCESS_TOKEN)
# trasnport
transport = wrapper.get_transport()
commit = client.commit.get(wrapper.stream_id, wrapper.commit_id)
print(dir(commit))
obj_id = commit.referencedObject
commit_data = operations.receive(obj_id, transport)

with input:
    selected_category = st.selectbox("Select category", commit_data.get_dynamic_member_names())

# parameters
parameters = commit_data[selected_category][0]["parameters"].get_dynamic_member_names()

with input:
    form = st.form("parameter_input")
    with form:
        selected_parameters = st.multiselect("Select Parameters", get_parameter_names(commit_data, selected_category))
        run_button = st.form_submit_button('RUN')

category_elements = commit_data[selected_category]

# Definations
def commit2viewer(stream, commit, branch_name=None):
    if branch_name:
        embed_src = "https://speckle.xyz/embed?stream=" + stream.id + "&commit=" + commit.id + "&branch=" + branch_name
    else:
        embed_src = "https://speckle.xyz/embed?stream=" + stream.id + "&commit=" + commit.id
    # print("Embed URL:", embed_src)  # Debugging statement
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
with input:
    # st.subheader("Commit URL of the below model")
    fetch_commitUrl = f"https://speckle.xyz/streams/{stream.id}/commits/{selected_commit.id}"
    # st.write(fetch_commitUrl)

with data:
    st.subheader("Data")
    result_data = []
    for element in category_elements:
        dict = {}
        for s_param in selected_parameters:
            get_parameter_by_name(element, s_param, dict)
        result_data.append(dict)
    result_DF = pd.DataFrame.from_dict(result_data)
    # show dataframe and add chatSpeckle feature
    col1, col2 = st.columns([1, 1])
    with col1:
        result = st.dataframe(result_DF)
    with col2:
        st.info("How can I help you?")
        OPENAI_API_KEY = st.text_input('OpenAI key', "sk-...vDlY")

        input_text = st.text_area('Enter your query')
        if input_text is not None:
            if st.button("Send"):
                st.info('Your query:' + input_text)
                result = chat_speckle(result_DF, input_text)
                st.success(result)

# Report
with report:
    st.subheader('Report')
    # Display some information about the selected stream and branch
    st.write(f"Selected Stream: {stream.name}")
    st.write(f"Commit URL of the model is {fetch_commitUrl}")
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
