# Package
# image processing and database 
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import time
import psycopg2

#----------------------****----------------------------#

#Image card pic convert to text format
def image_to_text(path):
    input_pic=Image.open(path)
    img_array=np.array(input_pic)

    reader=easyocr.Reader(['en'])
    text=reader.readtext(img_array,detail=0)
    return text

#----------------------****----------------------------#

# Extract data to text view
def extract_text(texts):
    extract_dic = {
        "Name": [],"Designation": [],"Company_Name": [],"Contact": [],"EMail": [],"Website": [],"Address": [],"Pincode": []}

    extract_dic["Name"].append(texts[0])
    lower = texts[1].lower()
    extract_dic["Designation"].append(lower)

    for i in range(2, len(texts)):
        if texts[i].startswith("+") or '-' in texts[i] or (texts[i].replace("-", " ").isdigit() and '-' in texts[i]):
            extract_dic["Contact"].append(texts[i])
            
        elif '@' in texts[i] and '.com' in texts[i]:
            extract_dic["EMail"].append(texts[i])
            
        elif 'www' in texts[i] or 'WWW' in texts[i] or 'wwW' in texts[i] or 'Www' in texts[i]:
            lower = texts[i].lower()
            extract_dic["Website"].append(lower)
            
        elif 'TamilNadu' in texts[i] or 'Tamil Nadu' in texts[i] or texts[i].isdigit():
            extract_dic["Pincode"].append(texts[i])
            
        elif re.match(r'^[A-Z a-z]', texts[i]):
            extract_dic["Company_Name"].append(texts[i])
            
        else:
            removeextra=re.sub(r'[,;]','',texts[i])
            extract_dic["Address"].append(removeextra)
            
    for key , value  in extract_dic.items():
        if len(value)>0:
            concad="".join(value)
            extract_dic[key]=[concad]
        else:
            value ="NA"
            extract_dic[key]=[value]         
            
    return extract_dic

#-----------------------****---------------------------#

# streamlit page creating 

# Menu Page option
st.set_page_config(page_title= "BizCardX",
                   page_icon= '💼',
                   layout= "wide",)

with st.sidebar:      

    selected = option_menu ("Menu", ['Home','Upload Image','View & Modify','Delete','Contact Us'], 
                        icons=['house','cloud-upload','gear','trash','phone'],
                        menu_icon="cast",
                        default_index=0,
                        styles={"icon": {"color": "orange", "font-size": "20px"},
                                "nav-link": {"font-size": "15px", "text-align": "left", "margin": "-2px", "--hover-color": "#FFFFFF"},
                                "nav-link-selected": {"background-color": "#225154"}})

# Few Description For Biz cards 
if selected == 'Home':
    st.header('Welcome To BizCardX:Extracting Business Card Data With OCR')
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



# Upload Image and Store Postgres With Table View Data   
if selected=="Upload Image":                  
    uploaded_files = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

    if uploaded_files is not None:
        st.image(uploaded_files,width=150)  
        
        text_img = image_to_text(uploaded_files)
        text_dict = extract_text(text_img)
        
        if text_dict:
            st.success("Text is Extracted Successfully")
            df = pd.DataFrame(text_dict)
            st.dataframe(df)
            
        button1=st.button(":red[Save Text]",use_container_width=True)
        
        if button1:            
            mydb = psycopg2.connect(host="localhost",
                user="postgres", password="12345",
                database="bizcard",port="5432")
            cursor = mydb.cursor()

            create_table = '''create table if not exists bizcard_details(
                                name varchar(99),designation varchar(99),
                                company_name varchar(99),contact varchar(99),
                                email varchar(99),website text,
                                address text,pincode varchar(99))'''

            cursor.execute(create_table)
            mydb.commit()            
            cursor = mydb.cursor()
            insert_data = '''insert into bizcard_details(name,designation,company_name,contact,
                                email,website,address,pincode) values(%s,%s,%s,%s,%s,%s,%s,%s)'''
            data =df.values.tolist()
            cursor.executemany(insert_data, data)
            mydb.commit()
            st.success("!!!Data Inserted Successfully!!!")

        
# Veiw The Database, Store in Postgres        
if selected=="View & Modify":                 
    selected_option = st.selectbox("Select Below Options", [ "Preview text", "Modify text"])
    if selected_option == "Select Below Options":
        pass
    elif selected_option == "Preview text":
                    mydb = psycopg2.connect(host="localhost",user="postgres", password="12345",
                                            database="bizcard",port="5432")
                    cursor = mydb.cursor()                
                    select_data="select * from bizcard_details"
                    cursor.execute(select_data)
                    table=cursor.fetchall()
                    mydb.commit()
                    table_df=pd.DataFrame(table,columns=("name","designation","company_name","contact","email","website","address","pincode"))
                    table_df

    # Data Details Can Edit and Modify The Details    
    elif selected_option == "Modify text":
                    mydb = psycopg2.connect(host="localhost",
                                            user="postgres", password="12345",
                                            database="bizcard",port="5432")
                    cursor = mydb.cursor()
                    select_data="select * from bizcard_details"
                    cursor.execute(select_data)
                    table=cursor.fetchall()
                    mydb.commit()
                    table_df=pd.DataFrame(table,columns=("name","designation","company_name","contact","email","website","address","pincode"))

                    select_name=st.selectbox("Select the Name",table_df["name"])
                    df3=table_df[table_df["name"]==select_name]
                
                    df4=df3.copy()
                    st.dataframe(df4)   
                    
                    coll1,coll2=st.columns(2)
                    with coll1:     
                        data_name=st.text_input("Name",df3["name"].unique()[0])      
                        data_design=st.text_input("Designation",df3["designation"].unique()[0])    
                        data_company=st.text_input("Company_name",df3["company_name"].unique()[0])    
                        data_contact=st.text_input("Contact",df3["contact"].unique()[0])  
                        
                        df4["name"]=data_name
                        df4["designation"]=data_design
                        df4["company_name"]=data_company
                        df4["contact"]=data_contact
                                        
        
                    with coll2:     
                        data_mail=st.text_input("Email",df3["email"].unique()[0])      
                        data_web=st.text_input("Website",df3["website"].unique()[0])    
                        data_address=st.text_input("Address",df3["address"].unique()[0])    
                        data_pincode=st.text_input("Pincode",df3["pincode"].unique()[0]) 
                        
                        df4["email"]=data_mail
                        df4["website"]=data_web
                        df4["address"]=data_address
                        df4["pincode"]=data_pincode
                    
                    st.dataframe(df4)    
                    
                    coll1, coll2 = st.columns(2)
                    with coll1:
                        button2 = st.button("Modify Text", use_container_width=True)
                        mydb = psycopg2.connect(host="localhost", user="postgres", password="12345", database="bizcard", port="5432")
                        cursor = mydb.cursor()

                    if button2:
                                            
                        cursor.execute(f"delete from bizcard_details where name='{select_data}'")
                        mydb.commit()

                        insert_data = '''insert into bizcard_details(name,designation,company_name,contact,email,website,address,pincode)
                                        values(%s,%s,%s,%s,%s,%s,%s,%s)'''
                        data = df4.values.tolist()
                        cursor.executemany(insert_data, data)
                        mydb.commit()
                        st.success("Above the Text data Modify Successfully")

# Unwanted Data Details Deleting Option                        
if selected == "Delete": 
    mydb = psycopg2.connect(host="localhost", user="postgres", password="12345", database="bizcard", port="5432")
    cursor = mydb.cursor()

    coll1, coll2 = st.columns(2)
    with coll1:
        select_data = "SELECT name FROM bizcard_details"
        cursor.execute(select_data)
        table5 = cursor.fetchall()
        mydb.commit()

        names = [i[0] for i in table5]
        name_select = st.selectbox("Select the Name", names)

        if st.button("Delete", use_container_width=True):
                delete_query = "DELETE FROM bizcard_details WHERE name = %s"
                cursor.execute(delete_query, (name_select,))
                mydb.commit()
                st.success("Deleted Successfully")

# Contact Deatil For Customer and Feedback To Company     
if selected==("Contact Us"):
    st.title("*:green[BizCardX]*")
    st.subheader("Contact Us")

    coll1, coll2 = st.columns(2)
    with coll1:
            st.subheader('Shibu')
            st.caption('Mobile:- 9944266277, E-Mail - shibu266277@gmail.com')
            st.caption('** Any Future Enquire Feel Free To Call Us **')
            st.caption(":orange [Note: * fill all mandatory fields]")     
            Name = st.text_input("Name*")
            Mobile = st.text_input("Mobile*")
            Email = st.text_input("Email*")
            Message = st.text_area("Message (optional)")

            if st.button("Submit"):
                st.success('''!!! Thank you for your Valuable comments & rating !!!''')

    with coll2:
            st.link_button("Git Hub", "https://en.wikipedia.org/wiki/GitHub")
            st.link_button("Linked in", "https://en.wikipedia.org/wiki/LinkedIn")
            st.link_button("Instagram", "https://en.wikipedia.org/wiki/Instagram")
            st.link_button("Whatsapp", "https://en.wikipedia.org/wiki/WhatsApp")
            st.link_button("E-Mail", "https://en.wikipedia.org/wiki/Email")     

#================================================xxx=============================================================#
