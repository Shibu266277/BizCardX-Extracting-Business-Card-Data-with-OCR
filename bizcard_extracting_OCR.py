# Package
# image_processing
import easyocr
from PIL import Image
import re
# database
import pandas as pd
from sqlalchemy import create_engine, update, MetaData, Table
# app
import os
import streamlit as st
from streamlit_option_menu import option_menu
import numpy as np
import PIL
from PIL import Image, ImageDraw
import cv2


# [Database library]
import sqlalchemy
import mysql.connector
from sqlalchemy import create_engine, inspect






# Upload image path code below:
def image_to_text(image_path):
    
    # Read the image
    image_img = Image.open(image_path)

    image_arr=np.array(image_img)

    reader= easyocr.Reader(['en'],gpu=False)
    text= reader.readtext(image_arr, detail=0)

    return text, image_img


# Extracted Bisz Card Data:
def extracted_text(texts):
   extrd_dict={"NAME":[], "DESIGNATION":[], "COMPANY":[], "CONTACT":[], "EMAIL":[], "WEBSITE":[],
               "ADDRESS":[], "PINCODE":[]}
   extrd_dict["NAME"].append(texts[0])
   extrd_dict["DESIGNATION"].append(texts[1])

   for i in range(2,len(texts)):
      if texts[i].startswith("+") or (texts[i].replace("-","").isdigit() and '-'in texts[i]):
         extrd_dict ["CONTACT"].append(texts[i])

      elif "@" in texts[i] and ".com" in texts[i]:
         extrd_dict["EMAIL"].append(texts[i])

      elif "www" in texts[i].lower() or "www" in texts[i].lower() or "www" in texts[i] or "www" in texts[i] or "www" in texts[i]:
         small=texts[i].lower()
         extrd_dict["WEBSITE"].append(small)

      elif "TamilNadu" in texts[i] or "TAMILNADU" in texts[i] or texts[i].isdigit():
         extrd_dict["PINCODE"].append(texts[i])

      elif re.match(r'^[A-Za-z]', texts[i]):
         extrd_dict["COMPANY"].append(texts[i])    

      else:
         remove_colon=re.sub(r'[,;]','',texts[i]) 
         extrd_dict["ADDRESS"].append(remove_colon)

   for key,value in extrd_dict.items():
      if len(value)>0:
         concadenate=" ".join(value)
         extrd_dict[key]=[concadenate]

      else:
         value = "NA"
         extrd_dict[key]= [value]

   return extrd_dict


def store_data(data):
    # Converting dictionary to DataFrame
    df = pd.DataFrame([data]) # Wrap data in a list to create DataFrame
    # Storing DataFrame in SQL table
    df.to_sql('business_card', if_exists='append', index=False)
    return df


# Streamlit Page FUNC:
st.set_page_config(page_title= "BizCardX",
                   page_icon= '💼',
                   layout= "wide",)

text = 'Extracting Business Card Data'   
st.markdown(f"<h2 style='color: white; text-align: center;'>{text} </h2>", unsafe_allow_html=True)


col1,col2 = st.columns([1,4])
with col1:
    menu = option_menu("Menu", ["Home","Upload","Database"], 
                    icons=["house",'cloud-upload', "list-task"],
                    menu_icon="cast",
                    default_index=0,
                    styles={"icon": {"color": "orange", "font-size": "20px"},
                            "nav-link": {"font-size": "15px", "text-align": "left", "margin": "-2px", "--hover-color": "#FFFFFF"},
                            "nav-link-selected": {"background-color": "#225154"}})
    if menu == 'Database':
        Database_menu = option_menu("Database", ['Modify','Delete'], 
                        
                        menu_icon="list-task",
                        default_index=0,
                        styles={"icon": {"color": "orange", "font-size": "20px"},
                                "nav-link": {"font-size": "15px", "text-align": "left", "margin": "0px", "--hover-color": "#FFFFFF"},
                                "nav-link-selected": {"background-color": "#225154"}})



with col2:
    if menu == 'Home':
        st.header('Welcome to BizCardX')
        home_text = ('This app helps you extract and manage business card details efficiently.')
        st.markdown(f"<h4 text-align: left;'>{home_text} </h4>", unsafe_allow_html=True)
        st.subheader(':orange[About the App:]')
        above_text = ('''BizCardX is a Streamlit web application designed for extracting information 
                     from business cards. It utilizes OCR (Optical Character Recognition) to extract 
                     text from uploaded images of business cards. The extracted details are then processed 
                     and organized into categories such as name, designation, contact information, company 
                     name, email, website, address, etc. Users can upload images of business cards, and the app 
                     extracts relevant information for storage and management.
                    ''')
                        
        st.markdown(f"<h4 text-align: left;'>{above_text} </h4>", unsafe_allow_html=True)
        st.subheader(":orange[Technologies Used:]")
        tech_text =(''' The app is built using Python and several libraries, including Streamlit for the web 
                    interface, EasyOCR for optical character recognition, and SQLAlchemy for database operations. 
                    The user interface is designed to be intuitive, allowing users to easily upload business card images, 
                    extract details, and manage the stored data. ''')
        st.markdown(f"<h4 text-align: left;'>{tech_text} </h4>", unsafe_allow_html=True)


    if menu == 'Upload':
        
        path = False
        col3,col4 = st.columns([2,2])
        with col3:
            uploaded_file = st.file_uploader("**Choose a file**", type=["jpg", "png", "jpeg"])
            
            if uploaded_file is not None:
                image_path = os.getcwd()+ "\\"+"Business Cards"+"\\"+ uploaded_file.name
                image = Image.open(image_path)
                col3.image(image)
                path = True

                extract = st.button("Extract")

                upload = st.button("Upload")
