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