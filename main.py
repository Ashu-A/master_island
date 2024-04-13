
import streamlit as st
import pandas as pd
from pandasai.llm.openai import OpenAI
import os
from specklepy.api.wrapper import StreamWrapper
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
from specklepy.api import operations
import plotly.express as px
import plotly.express as px
from pandasai import SmartDataframe


def chat_speckle(df, prompt):
    # llm = OpenAI(api_token="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")
    llm = OpenAI(api_token="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")
    # pandas_ai = PandasAI(llm, conversational=False)
    df = SmartDataframe(df, config={"llm": llm})
    result = df.chat(prompt)
    print(result)

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


header = st.container()
input = st.container()
data = st.container()
viewer = st.container()
report = st.container()
graphs = st.container()

with header:
    st.title('Island Chatbot')
    st.info('Hi I am ..... and I will help you to chat with the Island Team Revit model and I am using Speckle and OpenAI')


with input:
    st.subheader('Inputs')
    commit_url = st.text_input('Commit URL', "https://speckle.xyz/streams/06564bda95/commits/f308ed526e")
    serverCol, tokenCol = st.columns([1, 3])
    speckleServer = serverCol.text_input("Server URL", "speckle.xyz", help="Speckle server to connect.")
    speckleToken = tokenCol.text_input("Speckle token", "1c85ef40568298221924a2feca4e1eb2c42bf0c3a6")
    client = SpeckleClient(host=speckleServer)
    # Get account from Token
    account = get_account_from_token(speckleToken, speckleServer)
    # Authenticate
    client.authenticate_with_account(account)

    # Streams List👇
    streams = client.stream.list()
    # Get Stream Names
    streamNames = [s.name for s in streams]
    # Dropdown for stream selection
    sName = st.selectbox(label="Select your stream", options=streamNames, help="Select your stream from the dropdown")
    # SELECTED STREAM
    stream = client.stream.search(sName)[0]
    # Stream Branches 🌴
    branches = client.branch.list(stream.id)
    # Stream Commits 🏹
    commits = client.commit.list(stream.id, limit=100)


    def listToMarkdown(list, column):
        list = ["- " + i + " \n" for i in list]
        list = "".join(list)
        return column.markdown(list)


    # create a definition that creates iframe from commit id
    def commit2viewer(stream, commit, height=400) -> str:
        embed_src = "https://speckle.xyz/embed?stream=" + stream.id + "&commit=" + commit.id
        return st.components.v1.iframe(src=embed_src, height=height)




with viewer:
    st.subheader("Latest Commit")
    commit2viewer(stream, commits[0])


# wrapper
wrapper = StreamWrapper(commit_url)
# client
client = wrapper.get_client()
# trasnport
transport = wrapper.get_transport()

# get speckle commit
commit = client.commit.get(wrapper.stream_id, wrapper.commit_id)
# get object id from commit
obj_id = operations.send(base=diff_commit, transports=[transport])
# receive objects from commit
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
        st.info("⬇chatSpeckle⬇")
        OPENAI_API_KEY = st.text_input('OpenAI key', "sk-...vDlY")

        input_text = st.text_area('Enter your query')
        if input_text is not None:
            if st.button("Send"):
                st.info('Your query:' + input_text)
                result = chat_speckle(result_DF, input_text)
                st.success(result)
