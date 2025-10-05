import os 
import pandas as pd
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def insights(json_data):

    prompt = f"""
        You are a specialized Biomechanical Data Analyst. We already preprocessed EMG data and found out the following muscles are asymmetrical: Your task is to give me 2 exercises or stretches, a short description on how to perform each one, and a short reason behind each one.

        EMG Feature Analysis Results:
        - Tensor Fasciae Latae: 
        - Rectus Femoris: 
        - Vastus Lateralis: 
        - Tibialis Anterior: 
        - Soleus: 
        - Gastrocnemius: 
        - Biceps Femoris: 
        - Semitendinosus: 

        Response Format: 

        Here are 2 exercises you should try to solve the muscle imbalance:

        

    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )