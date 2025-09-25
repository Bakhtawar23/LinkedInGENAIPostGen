import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load from .env locally
load_dotenv()

# First try Streamlit secrets, then fallback to environment variable
groq_api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))

if not groq_api_key:
    raise ValueError("❌ GROQ_API_KEY not found. Please set it in Streamlit Secrets or .env file.")

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="meta-llama/llama-4-maverick-17b-128e-instruct"
)

if __name__ == "__main__":
    response = llm.invoke("Last winner of Asia Cup t20 format")
    print(response.content)