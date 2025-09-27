import streamlit as st 
import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns 
from modules.nav import navbar 

st.set_page_config(page_title='Job Market Dashboard', page_icon='📊', layout='wide')
st.title('Job Analyzer') 
st.write('Explore salary trends, skills demand, and real job postings across North America.')

navbar(); 

# st.text('Graph')
# st.markdown('## Header Level 2')

# st.success('Success')
# st.info('Information')
# st.warning('Warning')
# st.error('Error')

# exp = ZeroDivisionError('Trying to divide by 0')
# st.exception(exp)

# st.write('Text with write')
# st.write(range(10))

# if st.checkbox('Show/Hide'):
#     st.text('Showing the widget')

# status = st.radio('Select Gender:', ['Male', 'Female', 'Nonbinary', 'Prefer Not to Say'])
# if status == 'Male': 
#     st.success('Male')
# elif status == 'Female':
#     st.success('Female')
# elif status == 'Nonbinary':
#     st.success('Nonbinary')
# else: 
#     st.success('Prefer Not to Say')

# hobby = st.selectbox('Select a Hobby:', ['Dancing', 'Reading', 'Painting'])
# st.write('Your hobby is:', hobby)

# hobbies = st.multiselect('Select a Hobby:', ['Dancing', 'Reading', 'Painting'])
# st.write('You selected', len(hobbies), 'hobbies')

# st.button('Click Me')
# if st.button('About'): 
#     st.text('Welcome to DFP Job Analyzer')

# name = st.text_input('Enter your name', 'Type here...')
# if st.button('Submit'):
#     result = name.title()
#     st.success(result)

# level = st.slider('Choose a level', min_value=1, max_value=5)
# st.write(f'Selected level: {level}')

# # Title of the app
# st.title("BMI Calculator")

# # Input: Weight in kilograms
# weight = st.number_input("Enter your weight (kg):", min_value=0.0, format="%.2f")

# # Input: Height format selection
# height_unit = st.radio("Select your height unit:", ['Centimeters', 'Meters', 'Feet'])

# # Input: Height value based on selected unit
# height = st.number_input(f"Enter your height ({height_unit.lower()}):", min_value=0.0, format="%.2f")

# # Calculate BMI when button is pressed
# if st.button("Calculate BMI"):
#     try:
#         # Convert height to meters based on selected unit
#         if height_unit == 'Centimeters':
#             height_m = height / 100
#         elif height_unit == 'Feet':
#             height_m = height / 3.28
#         else:
#             height_m = height

#         # Prevent division by zero
#         if height_m <= 0:
#             st.error("Height must be greater than zero.")
#         else:
#             bmi = weight / (height_m ** 2)
#             st.success(f"Your BMI is {bmi:.2f}")

#             # BMI interpretation
#             if bmi < 16:
#                 st.error("You are Extremely Underweight")
#             elif 16 <= bmi < 18.5:
#                 st.warning("You are Underweight")
#             elif 18.5 <= bmi < 25:
#                 st.success("You are Healthy")
#             elif 25 <= bmi < 30:
#                 st.warning("You are Overweight")
#             else:
#                 st.error("You are Extremely Overweight")
#     except:
#         st.error("Please enter valid numeric values.")