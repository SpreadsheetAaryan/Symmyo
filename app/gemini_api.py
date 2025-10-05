import os 
import pandas as pd
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

raw_df = pd.read_csv('../preprocessed_data/preprocessed_emg_envelope.csv')

def insights(json_data):
    uploaded_csv = client.files.upload(file='../preprocessed_data/preprocessed_emg_envelope')

    prompt = f"""
        You are a specialized Biomechanical Data Analyst. Your task is to analyze EMG data from
        the iliacus and psoas (hip flexors) muscles during walking/exercise and provide actionable
        feedback.

        EMG Feature Analysis Results:
        - Left Iliacus Average Activation: {json_data['iliacus_left_avg']}
        - Right Iliacus Average Activation: {json_data['iliacus_right_avg']}
        - Iliacus Asymmetry Percentage: {json_data['asymmetry_iliacus']}% (Dominant Side: {"Right" if json_data['iliacus_right_avg'] > json_data['iliacus_left_avg'] else "Left"})

        - Left Psoas Average Activation: {json_data['psoas_left_avg']}
        - Right Psoas Average Activation: {json_data['psoas_right_avg']}
        - Psoas Asymmetry Percentage: {json_data['asymmetry_psoas']}% (Dominant Side: {"Right" if json_data['psoas_right_avg'] > json_data['psoas_left_avg'] else "Left"})

        Based on this data, perform the following:
        1. Biomechanical Interpretation: Explain what the asymmetry in the iliacus muscles means.
            Mention potential causes like tightness, weak antagonist, or gait imbalance.
        2. Specific Recommendations: Suggest 2 actionable stretches or mobility exercises
            specifically aimed at reducing the iliacus dominance.
        3. Format the response clearly using Markdown headings and lists.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )