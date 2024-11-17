import streamlit as st
import requests
from langchain_community.llms import Ollama


inp = st.text_input("prompt")
but = st.button("lets go")


if inp and but:
    try:
       
        response = requests.get("http://localhost:11434/status")
        if response.status_code == 200:
            llm = Ollama(model="qwen2.5")  
            s = llm(inp) 
            st.markdown(s)  
        else:
            st.error("Server is not available.")
    except requests.ConnectionError as e:
        st.error(f"Connection error: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")