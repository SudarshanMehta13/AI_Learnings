from dotenv import load_dotenv
load_dotenv() # loading all the environment variables

import streamlit as st
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

#function to load the chatbot
model=genai.GenerativeModel("gemini-pro")

def my_GeminiPro_chatBot(question):
    response = model.generate_content(question)
    return response.text

# initialize our streamlit app
st.set_page_config(page_title="Q&A demo")
st.header("My ChatBot")

input=st.text_input("Enter your query: ",key="input")
submit=st.button("Run")

#when submit is clicked

if submit:
    response= my_GeminiPro_chatBot(input)
    st.write(response)
    

