import streamlit as st
import os
from colorama import Style
from knowledge_base import doc_chat, load_embeddings, get_moderation

# Set an environment variable to suppress warnings
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Configure Streamlit app settings
st.set_page_config(
    layout="wide",
    page_title="Tempo-AI KB Information Retriever",
    page_icon="https://media.licdn.com/dms/image/C560BAQFB6iq1ExA1pg/company-logo_200_200/0/1678219677198?e=1704931200&v=beta&t=ZGwm2O0XqJtoCtWehbXPVBDI_FMtuIguym_x4q8aTSg"
)

# Hide the default "Made with Streamlit" footer
st.markdown('<style>footer {visibility: hidden;}</style>', unsafe_allow_html=True)

# Create a title container with an image and text
st.markdown('<div class="title-container"><img src="https://media.licdn.com/dms/image/C560BAQFB6iq1ExA1pg/company-logo_200_200/0/1678219677198?e=1704931200&v=beta&t=ZGwm2O0XqJtoCtWehbXPVBDI_FMtuIguym_x4q8aTSg" alt="Image" width="80"/><h1 class="title-text">Tempo-AI KB Information Retriever</h1></div>', unsafe_allow_html=True)

# Define the model name for the chatbot
model_name = "gpt-3.5-turbo"

def main():
    """
    Main function for the Conversational Doc Retriever Streamlit app.
    Handles user input, processes questions with a chatbot, and displays the conversation history.
    """
    # Create a chat input field for user questions
    question = st.text_input("What would you like to know?")

    if question:
        errors = get_moderation(question)
        if errors:
            st.write("Sorry, your question didn't pass the moderation check:")
            for error in errors:
                st.write(error)
                st.write(Style.RESET_ALL)

        # List of files and directory for document embeddings
        files = ["Ultimate_introduction_white_paper.pdf", "Planner-complete-guide-to-resource-planning.pdf"]
        persist_directory = "docs/chroma/"

        # Create a vector database for document embeddings
        vectordb = load_embeddings(persist_directory, files)

        # Process the user's question with the chatbot and get a response
        output = doc_chat(vectordb, model_name=model_name, question=question)

        # Initialize or retrieve the conversation history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display the conversation history
        for message in st.session_state.messages:
            with st.expander(message["role"]):
                st.markdown(message["content"])

        # Add the user's question to the conversation history
        st.session_state.messages.append({"role": "user", "content": question})
        with st.expander("User"):
            st.markdown(question)

        # Add the chatbot's response to the conversation history
        with st.expander("Assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown(output + "▌")
            message_placeholder.markdown(output)
        st.session_state.messages.append({"role": "assistant", "content": output})

if __name__ == '__main__':
    main()
