import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
import json
from gemini_api import insights

# --- Parameters ---
FS = 1000  # Sampling frequency in Hz

# --- Core Signal Processing Functions ---

def butter_bandpass(lowcut, highcut, fs, order=4):
    """Calculates Butterworth filter coefficients."""
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    # Btype='band' creates a bandpass filter
    b, a = butter(order, [low, high], btype='band')
    return b, a

def apply_filter(data, lowcut=20.0, highcut=499.0, fs=FS):
    """Applies the bandpass filter to the raw data using filtfilt (zero-phase shift)."""
    b, a = butter_bandpass(lowcut, highcut, fs)
    return filtfilt(b, a, data)

def rms_envelope(data, window_ms=200, fs=FS):
    """Calculates the Root Mean Square (RMS) envelope for smoothing."""
    # Convert window size from milliseconds to number of samples
    window_size = int(fs * window_ms / 1000)
    window_size = max(1, window_size) # ensure at least 1 sample

    # Custom RMS calculation function for rolling window
    def rms(arr):
        return np.sqrt(np.mean(arr**2))
    
    # Use rolling window on the data
    # center=True aligns the output to the middle of the window
    # min_periods=1 allows the calculation to start immediately
    return data.rolling(window=window_size, center=True, min_periods=1).apply(rms, raw=True)

def calculate_asymmetry(left, right):
    """Calculates percentage asymmetry based on the average activation."""
    # Asymmetry = (|R - L| / ((R + L) / 2)) * 100
    epsilon = 1e-6 # Avoid division by zero
    return ((right - left) / ( (right + left) / 2 + epsilon ) ) * 100

def preprocess_and_analyze(df, threshold, movement_start_ms=1000, movement_end_ms=4000):
    """
    Main function to run the full pipeline:
    Filter -> Rectify -> Smooth -> Feature Extraction.
    """
    processed_df = df.copy()
    muscles = ['tensor_fasciae_latae', 'rectus_femoris', 'vastus_lateralis', 'tibialis_anterior', 'soleus', 'gastrocnemius', 'biceps_femoris', 'semitendinosus']
    channels = [muscle + '_left' for muscle in muscles] + [muscle + '_right' for muscle in muscles]
    features = {}

    hash_map = {}

    for channel in channels:
        raw_data = df[channel].values
        
        # 1. Bandpass Filter (20-450 Hz)
        filtered_data = apply_filter(raw_data)
        
        # 2. Rectify (Absolute Value)
        rectified_data = np.abs(filtered_data)
        
        # 3. Smooth (RMS Envelope - 200 ms window)
        envelope_data = rms_envelope(pd.Series(rectified_data))
        processed_df[f'{channel}_envelope'] = envelope_data
        
        # 4. Feature Extraction
        # Isolate the data during the movement period
        movement_mask = (df['Time_ms'] >= movement_start_ms) & (df['Time_ms'] <= movement_end_ms)
        movement_envelope = envelope_data[movement_mask].dropna()
        
        # Calculate mean and peak activation for the movement
        features[f'{channel}_avg'] = movement_envelope.mean()
        features[f'{channel}_peak'] = movement_envelope.max()

    # 5. Asymmetry Calculation
    for muscle in muscles:
        asym_val = calculate_asymmetry(
            features[f'{muscle}_left_avg'],
            features[f'{muscle}_right_avg']
        )
        dominant = 'left' if asym_val < 0 else 'right'
        hash_map[muscle] = (asym_val, dominant)

    for muscle, val in hash_map.items():
        if val[0] > threshold:
            features[f'{muscle}_dominant_side'] = val[1]
            hash_map.pop(muscle)
            
    # Final JSON structure creation
    final_features = {muscle : val[1] for muscle, val in hash_map.items()}
    
    # You can also add peak values and dominant side to the JSON if needed
    
    return final_features, processed_df

# --- Execution ---

# 1. Load the Data
# NOTE: Replace 'raw_emg_data.csv' with your actual data file name
try:
    raw_df = pd.read_csv('../csv_data/dummy_data.csv')
except FileNotFoundError:
    print("Error: 'dummy_data.csv' not found. Please ensure your file is in the same directory.")
    exit()

# 2. Run the Analysis
# Assuming movement happened between 1000 ms and 4000 ms. Adjust these times 
# (in milliseconds) if your recording has different movement timings.
features_json, processed_df = preprocess_and_analyze(raw_df, 
                                                    movement_start_ms=1000, 
                                                    movement_end_ms=4000,
                                                    threshold=40)
# 3. Output Results

# Display the features ready for the Gemini API
print("\n--- Processed Metrics for Gemini API ---")
print(json.dumps(features_json, indent=2))

response = insights(features_json)
print(response)

# Save the processed data for Frontend Visualization
processed_df.to_csv('../preprocessed_data/processed_emg_envelope.csv', index=False)
print("\nProcessed envelope data saved to 'processed_emg_envelope.csv' for plotting/dashboard.")