from dotenv import load_dotenv
load_dotenv() # loading all the environment variables

import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

#function to load the chatbot
model=genai.GenerativeModel("gemini-pro-vision")

#funtion to describe an input image
def my_GeminiPro_ImageDescriptor(input,image):
    if input != "":
        response = model.generate_content([input,image])
    else:
        response = model.generate_content(image)
    return response.text

# initialize our streamlit app
st.set_page_config(page_title="Image Descriptor")
st.header("My Image Descriptor")

input=st.text_input("Enter your image input prompt text: ",key="input")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
image=""   
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Your uploaded image", use_column_width=True) # to display uploaded image


submit=st.button("Run")

## If ask button is clicked
if submit:
    response=my_GeminiPro_ImageDescriptor(input,image)
    st.write(response)