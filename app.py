from dotenv import load_dotenv
import base64
import streamlit as st
import os
import io
import PyPDF2 as pdf
import json
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_missing_keywords(resume_text, jd_text):
    # Tokenize the job description text
    jd_keywords = set(jd_text.lower().split())
    # Tokenize the resume text
    resume_keywords = set(resume_text.lower().split())
    # Identify missing keywords from JD in the resume
    missing_keywords = jd_keywords - resume_keywords
    return list(missing_keywords)

def summarize_job_description(jd_text):
    # Split job description into sentences
    sentences = jd_text.split('.')
    # Take the first few sentences as the summary
    summary = '. '.join(sentences[:3])  # Change the number to adjust summary length
    return summary

def get_gemini_repsonse(resume_text, jd_text, option):
    input_prompt = f"""
    Hey Act Like a skilled or very experienced ATS (Application Tracking System)
    with a deep understanding of the tech field, software engineering, data science,
    data analysis, and big data engineering. Your task is to evaluate the resume based
    on the given job description. You must consider the job market is very competitive
    and you should provide the best assistance for improving the resumes.
    Assign the percentage Matching based on JD and the missing keywords with high accuracy.
    resume:{resume_text}
    description:{jd_text}
    option:{option}

    I want the response in one single string having the structure
    {{"JD Match":"%","MissingKeywords":[],"Profile Summary":""}}
    """
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input_prompt)
    parsed_response = json.loads(response.text)
    
    if option == "Review Resume":
        return resume_text
    elif option == "%age Match":
        return f"The resume matches the job description by {parsed_response['JD Match']}."
    elif option == "Missing Elements":
        missing_elements = get_missing_keywords(resume_text, jd_text)
        if missing_elements:
            return f"The following elements are missing in the resume as required in the job description: {', '.join(missing_elements)}"
        else:
            return "All required elements are present in the resume."
    elif option == "Summarize JD":
        return summarize_job_description(jd_text)

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Set background color and padding
st.markdown(
    """
    <style>
    body {
        background-color: #add8e6; /* Light blue background */
        color: #333333;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton button {
        border-radius: 25px; /* Rounded border for buttons */
        width: 150px;
        padding: 10px 20px;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        background-color: #add8e6; /* Light blue color for buttons */
        color: white;
    }
    .stButton button:hover {
        background-color: #87ceeb; /* Darker blue color on hover */
    }
    .radio-button-container .css-hgdyqz {
        display: flex;
        flex-direction: row;
    }
    .radio-button-container .css-17e50e2 label {
        margin-right: 20px;
    }
    .footer {
        background-color: #add8e6; /* Light blue color */
        color: white;
        padding: 20px;
        text-align: center;
        border-radius: 10px;
    }
    .footer a {
        color: white;
        text-decoration: none;
        margin: 0 10px;
    }
    .line {
        width: 100%;
        margin-top: 10px;
        border-top: 1px solid white;
    }
    .powered-by {
        margin-top: 20px;
        font-size: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .powered-by img {
        width: 20px;
        height: 20px;
        margin-right: 5px;
    }
    .title {
        font-size: 36px; /* Increased font size */
        padding: 20px;
        border-radius: 15px;
        background-color: #add8e6; /* Light blue color for title */
        color: white;
        text-align: center;
        text-shadow: 2px 2px #333333; /* Adding text shadow effect */
    }
    .job-description {
        border-radius: 15px;
        padding: 20px;
        background-color: #ffffff; /* White color for job description */
        margin-bottom: 20px;
    }
    .upload-resume {
        border-radius: 15px;
        padding: 20px;
        background-color: #ffffff; /* White color for resume upload */
    }
    .image-container {
        margin-top: 20px; /* Added margin to create a gap */
        text-align: center;
    }
    .image-container img {
        margin-bottom: 20px; /* Added margin below the image */
    }
    .bright-text {
        font-weight: bold; /* Make text bold */
        color: #ff5733; /* Make text colorful */
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Image Container with Gap
st.markdown("<div class='image-container'><img src='https://media.geeksforgeeks.org/wp-content/uploads/20240108181204/Top-10-AI-Resume-Assessment-Tools-copy.webp' style='max-width: 100%;'></div>", unsafe_allow_html=True)

# Job Description Input
st.markdown("---")
st.subheader("Job Description")
jd = st.text_area("Paste the Job Description", height=100)

uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type="pdf", help="Please upload the PDF file of your resume.")

# Options Selection
st.markdown("---")
st.subheader("Select Option")
options = ["Review Resume", 
           "%age Match", 
           "Missing Elements", 
           "Summarize JD"]
selected_option = st.radio("", options, index=0)

# Analyze Button
st.markdown("---")
if st.button("Analyze", key="analyze_button"):  # Key added to the button to change color on each click
    if uploaded_file is not None and jd != "":
        resume_text = input_pdf_text(uploaded_file)
        response = get_gemini_repsonse(resume_text, jd, selected_option)
        st.subheader(response)
        if selected_option == "Review Resume":
            st.markdown("---")
            st.subheader("Resume Preview:")
            st.write(resume_text) # Display processed resume text
    else:
        st.warning("Please upload the resume and paste the job description before submitting.")

# Footer
# Image URL
image_url = "https://cdn.pixabay.com/photo/2023/08/15/14/05/banner-8192025_960_720.png"

# Image HTML
image_html = f'<img src="{image_url}" style="max-width: 100%; border-radius: 10px;">'

# Footer with Image and Light Blue Color
footer_with_image_light_blue = f"""
<div class="footer"> <!-- Light blue background color -->
    <div class="image-container">{image_html}</div> <!-- Moved the image to the footer -->
    <div class="line"></div>
    <div class="connect-text bright-text">Connect with me at</div> <!-- Added Connect with me text with bright color -->
    <a href="https://github.com/FasilHameed" target="_blank"><img src="https://img.icons8.com/plasticine/30/000000/github.png" alt="GitHub"></a>
    <a href="https://www.linkedin.com/in/faisal--hameed/" target="_blank"><img src="https://img.icons8.com/plasticine/30/000000/linkedin.png" alt="LinkedIn"></a>
    <a href="tel:+917006862681"><img src="https://img.icons8.com/plasticine/30/000000/phone.png" alt="Phone"></a>
    <a href="mailto:faisalhameed763@gmail.com"><img src="https://img.icons8.com/plasticine/30/000000/gmail.png" alt="Gmail"></a>
    <div class="line"></div>
    <div class="powered-by bright-text">Powered By <img src="https://img.icons8.com/clouds/30/000000/gemini.png" alt="Gemini"> Gemini 💫 and Streamlit 🚀</div> <!-- Bright color for powered by text -->
</div>
"""

# Render Footer with Image and Light Blue Color
st.markdown(footer_with_image_light_blue, unsafe_allow_html=True)
