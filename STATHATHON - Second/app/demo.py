import pandas as pd
import requests
import json


GEMINI_API_KEY = "AIzaSyAS_zRMtvMkgjp5MeTtMot4kJg4egyxtXw"
df = pd.read_csv(r"C:\Users\SAPTARSHI MONDAL\PycharmProjects\STATHATHON\uploads\FetusDataset.csv")
summary_dict = {
    "shape": df.shape,
    "columns": list(df.columns),
    "dtypes": df.dtypes.astype(str).to_dict(),
    "missing_values": df.isnull().sum().to_dict(),
    "basic_stats": df.describe(include='all').to_dict()
}

def normalize_text_to_list(text):
    if not text:
        return []
    # Split by newlines and strip empty entries
    return [line.strip() for line in text.split("\n") if line.strip()]

def generate_gemini_text(summary_dict):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }

    prompt = f"""
    You are a professional data analyst.
    Based on the dataset summary below, return a JSON object with the following keys:
    - executive_summary (string)
    - cleaning_notes (string)
    - recommendations (string)

    Dataset Summary:
    {summary_dict}

    Make sure your output is ONLY valid JSON.
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

        # Extract text from response
        if 'candidates' in data and len(data['candidates']) > 0:
            text_output = data['candidates'][0]['content']['parts'][0]['text']

            # Remove any potential JSON formatting characters
            text_output = text_output.strip()
            if text_output.startswith('```json'):
                text_output = text_output[7:]
            if text_output.endswith('```'):
                text_output = text_output[:-3]

            # Parse JSON safely
            try:
                parsed = json.loads(text_output)
                return parsed
            except json.JSONDecodeError as e:
                raise Exception(f"Invalid JSON format: {str(e)}\nReceived text: {text_output}")
        else:
            raise Exception("No valid response from Gemini API")

    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to generate analysis: {str(e)}")




try:
    ai_text = generate_gemini_text(summary_dict)
    executive_summary = ai_text.get("executive_summary", "")
    cleaning_notes = ai_text.get("cleaning_notes", "")
    recommendations = ai_text.get("recommendations", "")
    executive_summary_list = normalize_text_to_list(executive_summary)
    recommendations_list = normalize_text_to_list(recommendations)
    print(executive_summary_list)
    print(cleaning_notes)
    print(recommendations_list)

    #print(json.dumps(ai_text, indent=2))

except Exception as e:
    print(f"Error: {str(e)}")