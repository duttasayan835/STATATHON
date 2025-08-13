import requests
import os

GEMINI_API_KEY = "AIzaSyAS_zRMtvMkgjp5MeTtMot4kJg4egyxtXw"

def ask_gemini_question(summary_dict, question):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }

    prompt = f"""
    You are a data analysis assistant. Here is the dataset summary:
    {summary_dict}

    Question: {question}

    Please answer clearly and concisely based only on the dataset.
    """

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        if 'candidates' in data and data['candidates']:
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            return "No answer could be generated."
    except Exception as e:
        return f"Error: {str(e)}"
