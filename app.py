import streamlit as st
import warnings
from knowledge_base import *

# Set an environment variable to suppress warnings
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Ignore warnings
warnings.filterwarnings('ignore')

# Configure Streamlit app settings
st.set_page_config(layout="wide",
                   page_title="Tempo-AI KB Information Retriever",
                   page_icon="https://media.licdn.com/dms/image/C560BAQFB6iq1ExA1pg/company-logo_200_200/0/1678219677198?e=1704931200&v=beta&t=ZGwm2O0XqJtoCtWehbXPVBDI_FMtuIguym_x4q8aTSg"
                   )

# Hide the default "Made with Streamlit" footer
hide_default_format = """
       <style>
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

# Add your logo
st.image("tempo_logo.png", use_column_width=False)

# Set the title of the Streamlit app
st.title('Tempo-AI KB Information Retriever')

# Define the model name for the chatbot
model_name = "gpt-3.5-turbo"

# Create a chat input field for user questions
question = st.chat_input("What would you like to know?")

# List of files and directory for document embeddings
#files = ["Ultimate_introduction_white_paper.pdf", "Planner-complete-guide-to-resource-planning.pdf", "Documentation Links.docx"]
files = ["Ultimate_introduction_white_paper.pdf", "Planner-complete-guide-to-resource-planning.pdf"]
persist_directory = "docs/chroma/"

# Create a vector database for document embeddings
vectordb = create_embeddings(persist_directory, files)

def main():
    """
    Main function for the Conversational Doc Retriever Streamlit app.

    This function handles user input, processes questions with a chatbot,
    and displays the conversation history.

    Returns:
        None
    """
    global vectordb

    # Check if the user has entered a question
    if question:

        # Process the user's question with the chatbot and get a response
        output = doc_chat(vectordb,
                          model_name=model_name,
                          question=str(question)
                          )

        # Initialize or retrieve the conversation history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display the conversation history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Add the user's question to the conversation history
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        # Add the chatbot's response to the conversation history
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown(output + "▌")
            message_placeholder.markdown(output)
        st.session_state.messages.append({"role": "assistant", "content": output})

if __name__ == '__main__':
    main()