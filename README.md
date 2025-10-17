# Smart Resume Screener

A simple yet powerful web application built with Python (Flask) and Google's Gemini Pro API to automatically screen resumes against a job description. This tool provides a match score, a justification, and extracts key information like skills, experience, and education from the resume.

This project is designed to showcase skills in backend development, data processing, and AI API integration, making it a perfect portfolio piece for data analytics and data engineering roles.

***

## ✨ Features

* **Easy-to-Use Interface**: Simple web UI for uploading a PDF resume and pasting a job description.
* **AI-Powered Analysis**: Uses the Gemini 1.5 Pro model to intelligently parse and compare documents.
* **Match Score**: Generates a score from 1 to 10 indicating how well the resume matches the job requirements.
* **Detailed Justification**: Provides a concise summary explaining the score, highlighting strengths and weaknesses.
* **Structured Data Extraction**: Automatically extracts skills, work experience, and education into a clean, structured format.
* **Single-File Application**: The entire application (backend and frontend) is contained within a single Python file for simplicity.

***

## 🛠️ Tech Stack

* **Backend**: Python, Flask
* **AI Model**: Google Gemini 1.5 Pro
* **PDF Parsing**: PyPDF2
* **Frontend**: HTML, Tailwind CSS, JavaScript

***

## 🚀 How to Run it Locally?

Follow these steps to run the application on your local machine.

### 1. Prerequisites
Make sure you have **Python 3.8** or higher installed on your system.

### 2. Project Files
Create a folder for your project and add the following two files inside it:
* `app.py` (The Python code for the application)
* `requirements.txt`

### 3. Create a Virtual Environment
It's a best practice to use a virtual environment to manage project dependencies.

```bash
# Create a virtual environment named 'venv'
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

part 4:
pip install -r requirements.txt

export GOOGLE_API_KEY="PASTE_YOUR_API_KEY_HERE"  (For Mac)
set GOOGLE_API_KEY="PASTE_YOUR_API_KEY_HERE"(for WINDOWS)

## now run the application
python app.py


