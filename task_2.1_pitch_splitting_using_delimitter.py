pip install google-generativeai

import os
import re
import google.generativeai as genai
from tqdm import tqdm
import nltk

# Ensure that NLTK punkt is downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Ensure that NLTK punkt_tab is downloaded
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')


def extract_pitches_gemini(transcript_path, output_dir, api_key):
    # Initialize the Gemini Pro model
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Read the transcript
    with open(transcript_path, 'r', encoding='utf-8') as file:
        transcript = file.read()

    # Replace unknown characters
    text_chunk = transcript.encode('utf-8', errors='replace').decode('utf-8')

    # Refined Prompt for Gemini
    prompt = f"""
        You are an expert in analyzing reality show transcripts, especially from shows like Shark Tank or Dragon's Den. Your task is to identify and extract individual business pitches, along with the immediate follow-up questions asked by the investors (Sharks or Dragons).

        A business pitch begins when an entrepreneur starts describing their business idea and usually includes:
        - The problem they are solving.
        - Their product or service solution.
        - Their business model, revenue projections, and any metrics.
        - The investment they are seeking.
        - Any financial information they provide.

        Include in your output:
        Task: Automated Pitch Extraction from Reality Show Subtitles

Extract individual business pitches from subtitles of reality shows like Shark Tank, where each episode may feature multiple pitches.

Goal: Break down longer episodes into separate files, each containing a single pitch, to utilize the best language model without exceeding context length limits.

Steps:

     - Provide subtitles for episodes with multiple pitches.
     - Use a context model to automatically separate the text into individual pitches.
     - Create separate files for each pitch, containing only the text for that specific business pitch and corresponding questions.

Example: For an episode with 4 businesses pitching, the output should be 4 separate files, each with the pitch and questions for only one business. This approach minimizes the text given to the model, allowing for optimal performance without requiring a paid account upgrade.

Let me know if you have any questions.
not that important, ideally text so we can easily use it as an input for another LLM query.

The goal is to break the episodes into individual pitches (using large context LLMs) so we have smaller files to feed to the best performing LLM for extracting the questions and other details without hitting the context ceiling.

If the original subtile file name is "SharkTankS11E14.txt", then the individual pitch files will be:

SharkTankS11E14_pitch_1.txt
SharkTankS11E14_pitch_2.txt
.**

        Transcript:
        ```
        {text_chunk}
        ```

        Please note:
         - 
    """

    # Generate content using Gemini
    try:
        response = model.generate_content(prompt)
        all_pitches = response.text
    except Exception as e:
        print(f"Error generating with Gemini: {e}")
        return

    # Create output files
    base_name = os.path.splitext(os.path.basename(transcript_path))[0]

    # Split pitches using the delimiter
    pitch_candidates = re.split(r'======== NEXT PITCH ========', all_pitches)
    pitches = [pitch.strip() for pitch in pitch_candidates if pitch.strip()]
    # Ensure there are any pitches
    if pitches:
        for i, pitch in enumerate(pitches):
            output_filename = os.path.join(output_dir, f"{base_name}_pitch_{i + 1}.txt")
            with open(output_filename, 'w', encoding='utf-8') as outfile:
                outfile.write(pitch)
            print(f"Saved pitch to {output_filename}")
    else:
        print(f"No pitches found in transcript {transcript_path}")


# Setup input and output folders
input_folder = r"C:\Users\adhil\OneDrive\Documents\cleaned_txt"  # Replace with the actual path to your transcripts folder
output_folder = r"C:\Users\adhil\OneDrive\Documents\letsgetmoving-project\task-2\new_gemiin_delimiter"  # Replace with desired output folder
api_key = "AIzaSyD_2hNhwOqZP0MMqFcB4tQCDFL1Rw4_ONI" # Replace with your actual API key

# Get a list of already processed files based on the output directory
processed_files = set()
for filename in os.listdir(output_folder):
    if filename.endswith(".txt") and "_pitch_" in filename:
        base_name = filename.split("_pitch_")[0]
        processed_files.add(base_name)

# Iterate over files in the input folder
for filename in tqdm(os.listdir(input_folder), desc="Processing Files"):
    if filename.endswith(".txt"):
        transcript_path = os.path.join(input_folder, filename)
        base_name = os.path.splitext(filename)[0]

        # Skip if already processed
        if base_name in processed_files:
            print(f"Skipping processed file: {filename}")
            continue

        extract_pitches_gemini(transcript_path, output_folder, api_key)
        
print("Finished processing all files!")

