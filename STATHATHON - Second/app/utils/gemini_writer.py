import requests
import os
from dotenv import load_dotenv
import json

GEMINI_API_KEY = "AIzaSyAS_zRMtvMkgjp5MeTtMot4kJg4egyxtXw"

def generate_gemini_text(summary_dict):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"  # Example Grok endpoint
    headers = {
        "Content-Type": "application/json"
    }

    prompt = f"""
    You are a professional data analyst.
    Based on the dataset summary below, produce a JSON with the following fields:
    - introduction
    - methods
    - executive_summary (list of bullet points)
    - cleaning_notes
    - conclusion
    - recommendations (list of bullet points)

    Dataset Summary:
    {summary_dict}

    Respond ONLY in valid JSON format.
    """

    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        if 'candidates' in data and data['candidates']:
            text_output = data['candidates'][0]['content']['parts'][0]['text']

            # Clean the text output - remove markdown formatting if present
            text_output = text_output.replace('```json', '').replace('```', '').strip()

            # Parse JSON
            parsed = json.loads(text_output)

            # Ensure all required fields exist
            required_fields = ['introduction', 'methods', 'executive_summary',
                               'cleaning_notes', 'conclusion', 'recommendations']
            for field in required_fields:
                if field not in parsed:
                    parsed[field] = [] if field in ['executive_summary', 'recommendations'] else ""

            return parsed
        else:
            raise Exception("No valid candidates in response")
    except Exception as e:
        raise Exception(f"Failed to generate analysis: {str(e)}")

