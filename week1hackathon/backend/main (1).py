import fitz  # PyMuPDF
from apify_client import ApifyClient
import openai

# Function to convert PDF to text
def pdf_to_text(pdf_path):
    document = fitz.open(pdf_path)
    text = ""
    for page_num in range(document.page_count):
        page = document.load_page(page_num)
        text += page.get_text()
        text += '\n' + ('-' * 80) + '\n'
    return text

# Function to get job listings using Apify
def get_job_listings(api_token, task_id):
    client = ApifyClient(api_token)
    run = client.task(task_id).call()
    job_listings = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        job_listings.append(item)
    return job_listings

# Function to interact with OpenAI API
def get_gpt3_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.5,
    )
    return response.choices[0].message["content"].strip()

# Function to extract sections from text using OpenAI
def extract_with_llm(text, section):
    prompt = f"Extract the {section} from the following text:\n\n{text}"
    return get_gpt3_response(prompt)

# Function to preprocess text using OpenAI
def preprocess_with_llm(text):
    prompt = f"Preprocess the following text for feature extraction:\n\n{text}"
    return get_gpt3_response(prompt)

# Function to evaluate section match score using OpenAI
def evaluate_section(resume_section, job_section, section_name):
    prompt = f"Evaluate how well the following resume {section_name} matches the job {section_name}:\n\nResume {section_name}:\n{resume_section}\n\nJob {section_name}:\n{job_section}\n\nProvide a match score from 0 to 100 and a brief explanation."
    response = get_gpt3_response(prompt)
    score_str = response.split()[-1]
    score_str = ''.join(filter(str.isdigit, score_str))
    score = int(score_str) if score_str else 0
    explanation = response.rsplit(' ', 1)[0]
    return score, explanation

# Function to calculate match score between resume and job description
def calculate_match_score(resume_text, job_description):
    skills = extract_with_llm(resume_text, "Skills")
    experience = extract_with_llm(resume_text, "Experience")
    education = extract_with_llm(resume_text, "Education")

    cleaned_skills = preprocess_with_llm(skills)
    cleaned_experience = preprocess_with_llm(experience)
    cleaned_education = preprocess_with_llm(education)

    job_skills = extract_with_llm(job_description, "Skills")
    job_experience = extract_with_llm(job_description, "Experience")
    job_education = extract_with_llm(job_description, "Education")

    cleaned_job_skills = preprocess_with_llm(job_skills)
    cleaned_job_experience = preprocess_with_llm(job_experience)
    cleaned_job_education = preprocess_with_llm(job_education)

    skill_score, skill_explanation = evaluate_section(cleaned_skills, cleaned_job_skills, "skills")
    experience_score, experience_explanation = evaluate_section(cleaned_experience, cleaned_job_experience, "experience")
    education_score, education_explanation = evaluate_section(cleaned_education, cleaned_job_education, "education")

    total_match_score = (skill_score + experience_score + education_score) / 3

    print(f"Skill Score: {skill_score}")
    print(f"Experience Score: {experience_score}")
    print(f"Education Score: {education_score}")
    print(f"Total Match Score: {total_match_score}")

    return total_match_score, skill_explanation, experience_explanation, education_explanation

# Example usage
pdf_path = './zoubida_Resume_4FM_2024.pdf'
resume_text = pdf_to_text(pdf_path)

api_token = ""
task_id = ""
job_listings = get_job_listings(api_token, task_id)

openai.api_key = ''

# Process job listings and calculate match scores
output_lines = []
for job in job_listings:
    job_description = job.get('description', '')
    total_match_score, skill_explanation, experience_explanation, education_explanation = calculate_match_score(resume_text, job_description)
    output_lines.append(f"Job Title: {job.get('title', 'N/A')}")
    output_lines.append(f"Company: {job.get('company', 'N/A')}")
    output_lines.append(f"Link: {job.get('link', 'N/A')}")
    output_lines.append(f"Match Score: {total_match_score}")
    output_lines.append(f"Skill Match Explanation: {skill_explanation}")
    output_lines.append(f"Experience Match Explanation: {experience_explanation}")
    output_lines.append(f"Education Match Explanation: {education_explanation}")
    output_lines.append('\n' + ('-' * 80) + '\n')

# Save the output to text files
with open('job_matches.txt', 'w', encoding='utf-8') as file:
    file.write('\n'.join(output_lines))

with open('job_links.txt', 'w', encoding='utf-8') as file:
    for job in job_listings:
        file.write(f"{job.get('link', 'N/A')}\n")

with open('company_names.txt', 'w', encoding='utf-8') as file:
    for job in job_listings:
        file.write(f"{job.get('company', 'N/A')}\n")
