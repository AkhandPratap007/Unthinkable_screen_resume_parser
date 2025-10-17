# Smart Resume Screener - Full Application in a Single File
# This file contains both the Python Flask backend and the HTML/CSS/JS frontend.
# FINAL VERSION: Includes the confirmed working API key.

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import PyPDF2
import io
import os
import json
import google.generativeai as genai

# --- 1. FRONTEND CODE ---
# The entire HTML, CSS, and JavaScript for the user interface is stored in this variable.
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Resume Screener</title>
    <!-- Tailwind CSS for modern styling -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Custom Font -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
        }
        /* Simple spinner animation */
        .loader {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body class="bg-gray-50 text-gray-800">

    <div class="container mx-auto p-4 md:p-8 max-w-4xl">
        
        <header class="text-center mb-8">
            <h1 class="text-4xl font-bold text-gray-900">Smart Resume Screener</h1>
            <p class="text-md text-gray-600 mt-2">Upload a resume and job description to get an AI-powered match analysis.</p>
        </header>

        <!-- Main Form Card -->
        <div class="bg-white p-6 md:p-8 rounded-xl shadow-lg border border-gray-200">
            <form id="screen-form">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Job Description Input -->
                    <div class="md:col-span-1">
                        <label for="job_description" class="block text-sm font-medium text-gray-700 mb-2">Job Description</label>
                        <textarea id="job_description" name="job_description" rows="10" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition" placeholder="Paste the full job description here..."></textarea>
                    </div>
                    <!-- Resume Upload -->
                    <div class="md:col-span-1">
                        <label for="resume" class="block text-sm font-medium text-gray-700 mb-2">Upload Resume (PDF)</label>
                        <div class="flex items-center justify-center w-full">
                            <label for="resume-upload" class="flex flex-col items-center justify-center w-full h-full border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition">
                                <div class="flex flex-col items-center justify-center pt-5 pb-6 px-4">
                                    <svg class="w-8 h-8 mb-4 text-gray-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/></svg>
                                    <p class="mb-2 text-sm text-gray-500"><span class="font-semibold">Click to upload</span> or drag and drop</p>
                                    <p class="text-xs text-gray-500">PDF only</p>
                                    <p id="file-name" class="text-xs text-blue-600 mt-2 font-medium"></p>
                                </div>
                                <input id="resume-upload" name="resume" type="file" class="hidden" accept=".pdf" />
                            </label>
                        </div> 
                    </div>
                </div>
                <!-- Submit Button -->
                <div class="mt-6 text-center">
                    <button type="submit" class="w-full md:w-auto bg-blue-600 text-white font-bold py-3 px-8 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-300 transition-all duration-300 transform hover:scale-105">
                        Screen Resume
                    </button>
                </div>
            </form>
        </div>

        <!-- Loading, Error, and Results Section -->
        <div id="status-container" class="mt-8">
            <!-- Loader -->
            <div id="loader" class="hidden flex justify-center items-center">
                <div class="loader"></div>
            </div>
            <!-- Error Message -->
            <div id="error-message" class="hidden text-center bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg" role="alert">
            </div>
            <!-- Results -->
            <div id="results-container" class="hidden bg-white p-6 md:p-8 rounded-xl shadow-lg border border-gray-200">
                <!-- Results will be dynamically inserted here -->
            </div>
        </div>
    </div>

    <script>
        const screenForm = document.getElementById('screen-form');
        const resumeUploadInput = document.getElementById('resume-upload');
        const fileNameDisplay = document.getElementById('file-name');
        const loader = document.getElementById('loader');
        const errorMessage = document.getElementById('error-message');
        const resultsContainer = document.getElementById('results-container');

        resumeUploadInput.addEventListener('change', () => {
            fileNameDisplay.textContent = resumeUploadInput.files.length > 0 ? resumeUploadInput.files[0].name : '';
        });

        screenForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(screenForm);
            
            if (!formData.get('resume').size || !formData.get('job_description')) {
                displayError('Please provide both a job description and a resume file.');
                return;
            }

            loader.style.display = 'flex';
            errorMessage.style.display = 'none';
            resultsContainer.style.display = 'none';

            try {
                // The fetch URL is now a relative path, as the page is served from the same origin as the API.
                const response = await fetch('/screen_resume', {
                    method: 'POST',
                    body: formData,
                });
                
                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'An unknown error occurred.');
                }
                
                displayResults(data);

            } catch (error) {
                console.error('Error screening resume:', error);
                displayError(error.message);
            } finally {
                loader.style.display = 'none';
            }
        });

        function displayError(message) {
            errorMessage.textContent = `Error: ${message}`;
            errorMessage.style.display = 'block';
            resultsContainer.style.display = 'none';
        }

        function getScoreColor(score) {
            if (score >= 80) return 'bg-green-500';
            if (score >= 50) return 'bg-yellow-500';
            return 'bg-red-500';
        }
        
        function displayResults(data) {
            resultsContainer.innerHTML = ''; 
            const { match_score, justification, parsed_resume } = data;

            resultsContainer.innerHTML = `
                <h2 class="text-2xl font-bold text-center mb-6">Screening Results</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="md:col-span-1 flex flex-col items-center text-center">
                         <h3 class="text-lg font-semibold mb-3">Match Score</h3>
                         <div class="w-32 h-32 rounded-full ${getScoreColor(match_score)} flex items-center justify-center text-white text-5xl font-bold shadow-lg">
                            ${match_score}<span class="text-2xl mt-3">/10</span>
                         </div>
                         <h3 class="text-lg font-semibold mt-6 mb-2">Justification</h3>
                         <p class="text-sm text-gray-600">${justification}</p>
                    </div>
                    <div class="md:col-span-2">
                        <h3 class="text-lg font-semibold mb-3 text-center md:text-left">Extracted Information</h3>
                        <div class="mb-4">
                            <h4 class="font-semibold text-gray-800">Skills</h4>
                            <div class="flex flex-wrap gap-2 mt-2">
                                ${parsed_resume.skills && parsed_resume.skills.length > 0
                                    ? parsed_resume.skills.map(skill => `<span class="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-1 rounded-full">${skill}</span>`).join('')
                                    : '<p class="text-sm text-gray-500">No skills extracted.</p>'
                                }
                            </div>
                        </div>
                        <div class="mb-4">
                            <h4 class="font-semibold text-gray-800">Experience</h4>
                            <ul class="list-disc list-inside mt-2 space-y-2">
                                ${parsed_resume.experience && parsed_resume.experience.length > 0
                                    ? parsed_resume.experience.map(exp => `<li><strong>${exp.title}</strong> at ${exp.company} (${exp.duration})</li>`).join('')
                                    : '<p class="text-sm text-gray-500">No experience extracted.</p>'
                                }
                            </ul>
                        </div>
                        <div>
                            <h4 class="font-semibold text-gray-800">Education</h4>
                            <ul class="list-disc list-inside mt-2 space-y-2">
                                ${parsed_resume.education && parsed_resume.education.length > 0
                                    ? parsed_resume.education.map(edu => `<li><strong>${edu.degree}</strong> from ${edu.institution}</li>`).join('')
                                    : '<p class="text-sm text-gray-500">No education extracted.</p>'
                                }
                            </ul>
                        </div>
                    </div>
                </div>
            `;
            resultsContainer.style.display = 'block';
            errorMessage.style.display = 'none';
        }
    </script>
</body>
</html>
"""

# --- 2. BACKEND LOGIC ---
# Initialize the Flask application
app = Flask(__name__)
CORS(app)

# --- FINAL API KEY CONFIGURATION ---
try:
    # Your confirmed working API key is now in the code.
    API_KEY = "AIzaSyDTzCLurd_BdayX9bUr29xx1AM7TTdq_gg"
    
    # This check ensures you don't accidentally run with the placeholder.
    if API_KEY == "PASTE_YOUR_API_KEY_HERE":
        print("!!! ERROR: Please paste your API key into the app.py file. !!!")
    else:
        genai.configure(api_key=API_KEY)
        print(">>> Gemini API key configured successfully. The server is ready. <<<")

except Exception as e:
    print(f"ERROR: Could not configure Gemini API. Details: {e}")
# --- END OF CHANGE ---


# CORRECTED MODEL NAME
model = genai.GenerativeModel('gemini-2.5-pro')

def extract_text_from_pdf(file_stream):
    """Helper function to extract text from a PDF file stream."""
    try:
        pdf_reader = PyPDF2.PdfReader(file_stream)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

# API Endpoint to serve the Frontend
@app.route('/')
def index():
    """Serves the main HTML page."""
    return Response(HTML_CONTENT, mimetype='text/html')

# API Endpoint for Resume Screening
@app.route('/screen_resume', methods=['POST'])
def screen_resume():
    """Screens a resume against a job description using Gemini."""
    if 'resume' not in request.files or 'job_description' not in request.form:
        return jsonify({'error': 'Missing resume or job description'}), 400

    resume_file = request.files['resume']
    job_description = request.form['job_description']

    if resume_file.filename == '' or not resume_file.filename.endswith('.pdf'):
        return jsonify({'error': 'Invalid or missing PDF file'}), 400

    pdf_in_memory = io.BytesIO(resume_file.read())
    resume_text = extract_text_from_pdf(pdf_in_memory)

    if resume_text is None:
        return jsonify({'error': 'Failed to extract text from the PDF'}), 500

    prompt = f"""
    You are an expert HR recruitment assistant specializing in technical roles.
    Your task is to analyze the following resume text and compare it against the provided job description.

    First, parse the resume text into a structured JSON format with the following keys: "skills", "experience", and "education".
    Then, compare the parsed resume to the job description and calculate a match score from 1 to 10.
    Finally, provide a concise justification for your score.

    Return a single, valid JSON object with the following structure and nothing else:
    {{
      "parsed_resume": {{
        "skills": ["skill1", "skill2", ...],
        "experience": [
          {{"title": "Job Title", "company": "Company Name", "duration": "Years"}},
          ...
        ],
        "education": [
          {{"degree": "Degree", "institution": "Institution Name"}}
        ]
      }},
      "match_score": <number from 1 to 100>,
      "justification": "<A concise paragraph explaining the score, highlighting matching skills and experience gaps.>"
    }}

    --- RESUME TEXT ---
    {resume_text}

    --- JOB DESCRIPTION ---
    {job_description}
    """

    try:
        response = model.generate_content(prompt)
        cleaned_response_text = response.text.replace('```json', '').replace('```', '').strip()
        analysis_result = json.loads(cleaned_response_text)
        return jsonify(analysis_result)

    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from Gemini response.")
        print("Raw Response:", response.text)
        return jsonify({'error': 'Failed to parse the analysis from the AI model'}), 500
    except Exception as e:
        print(f"An error occurred with the Gemini API: {e}")
        return jsonify({'error': 'An error occurred while analyzing the resume'}), 500

# Run the application
if __name__ == '__main__':
    app.run(debug=True, port=5000)

