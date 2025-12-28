# To call watsonx's LLM, we need to import the library of IBM Watson Machine Learning
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from ibm_watson_machine_learning.foundation_models import Model

# Project ID for Skills Network labs (or your own project)
PROJECT_ID = "skills-network"

# Define the credentials for watsonx.ai
credentials = {
    "url": "https://us-south.ml.cloud.ibm.com"
}

# Specify model_id that will be used for inferencing
model_id = "mistralai/mistral-medium-2505"

# Define the model parameters
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.utils.enums import DecodingMethods

parameters = {
    GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
    GenParams.MIN_NEW_TOKENS: 1,
    GenParams.MAX_NEW_TOKENS: 1024
}

# Define the LLM
model = Model(
    model_id=model_id,
    params=parameters,
    credentials=credentials,
    project_id=PROJECT_ID
)

import requests

def speech_to_text(audio_binary):
    # Watson Speech to Text endpoint (US South region)
    base_url = "https://api.us-south.speech-to-text.watson.cloud.ibm.com"
    api_url = base_url + "/v1/recognize"

    params = {
        'model': 'en-US_Multimedia',  # Change if you need another language model
    }

    headers = {
        'Content-Type': 'audio/wav',  # Browser recordings are often webm/opus; adjust if needed
    }

    # Replace with your actual Speech to Text service apikey
    auth = ('apikey', 'YOUR_STT_APIKEY_HERE')

    response = requests.post(api_url, params=params, headers=headers, data=audio_binary, auth=auth)

    if response.status_code != 200:
        print('Speech-to-Text error:', response.status_code, response.text)
        return "Error in speech recognition"

    result = response.json()

    if not result.get('results'):
        print('No transcription results')
        return ""

    # Get the best transcript
    text = result['results'][0]['alternatives'][0]['transcript']
    print('Recognized text:', text)
    return text


def text_to_speech(text, voice=""):
    # Watson Text to Speech endpoint (US South region)
    base_url = "https://api.us-south.text-to-speech.watson.cloud.ibm.com"
    api_url = base_url + "/v1/synthesize"

    # Default to a Spanish voice since we're translating to Spanish
    selected_voice = voice if voice and voice != "default" else "es-ES_EnriqueV3Voice"

    params = {
        'voice': selected_voice,
    }

    headers = {
        'Accept': 'audio/wav',
        'Content-Type': 'application/json',
    }

    json_data = {
        'text': text,
    }

    # Replace with your actual Text to Speech service apikey
    auth = ('apikey', 'YOUR_TTS_APIKEY_HERE')

    response = requests.post(api_url, headers=headers, json=json_data, params=params, auth=auth)

    print('Text-to-Speech response status:', response.status_code)

    if response.status_code != 200:
        print('TTS Error:', response.text)
        return b''  # Return empty bytes on error

    return response.content


def watsonx_process_message(user_message):
    # Strict translation prompt
    prompt = f"""Translate the following English sentence into Spanish. 
Reply ONLY with the translation, no explanations, no formatting, no extra text.

English: {user_message}
Spanish:"""

    response_text = model.generate_text(prompt=prompt)
    print("watsonx response:", response_text)
    return response_text.strip()