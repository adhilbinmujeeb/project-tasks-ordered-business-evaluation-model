import os
import re

def split_pitch_files(input_folder, output_folder):
    """
    Splits pitch files into individual pitch files based on keywords.

    Args:
        input_folder (str): Path to the folder containing the input files.
        output_folder (str): Path to the folder where output files will be created.
    """

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_folder, filename)
            with open(input_path, 'r', encoding='utf-8') as infile:
                content = infile.read()

            # Regex to match the start of a pitch text file
            pitch_separator = re.compile(r"^(SharkTankS\d+E\d+_pitch_\d+\.txt)", re.MULTILINE)
            
            # Find the start of each pitch using the regex
            matches = list(pitch_separator.finditer(content))
            
            if not matches:
                print(f"No pitch markers found in {filename}, skipping.")
                continue

            # Loop through matches and extract content
            for i, match in enumerate(matches):
              start_index = match.start()
              
              if i+1 < len(matches):
                end_index = matches[i+1].start()
              else:
                  end_index = len(content)

              pitch_content = content[start_index:end_index].strip()
              pitch_filename = match.group(1)
              output_path = os.path.join(output_folder, pitch_filename)
              with open(output_path, 'w', encoding='utf-8') as outfile:
                  outfile.write(pitch_content)
              print(f"Created {pitch_filename}")


if __name__ == "__main__":
    input_folder = r"C:\Users\adhil\OneDrive\Documents\letsgetmoving-project\task-2\new_gemiin_delimiter"  # Replace with the path to your input folder
    output_folder = r"C:\Users\adhil\OneDrive\Documents\letsgetmoving-project\task-2\experiment_out"  # Replace with the path to your output folder
    split_pitch_files(input_folder, output_folder)


import os
import re

def split_pitch_files(input_folder, output_folder):
    """
    Splits pitch files into individual pitch files based on keywords, preventing overwriting.

    Args:
        input_folder (str): Path to the folder containing the input files.
        output_folder (str): Path to the folder where output files will be created.
    """

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_folder, filename)
            with open(input_path, 'r', encoding='utf-8') as infile:
                content = infile.read()

            # Regex to match the start of a pitch text file
            pitch_separator = re.compile(r"^(SharkTankS\d+E\d+_pitch_\d+\.txt)", re.MULTILINE)

            # Find the start of each pitch using the regex
            matches = list(pitch_separator.finditer(content))

            if not matches:
                print(f"No pitch markers found in {filename}, skipping.")
                continue
            
            file_counter = {}  # Dictionary to track the counter for each filename

            # Loop through matches and extract content
            for i, match in enumerate(matches):
              start_index = match.start()

              if i+1 < len(matches):
                  end_index = matches[i+1].start()
              else:
                  end_index = len(content)

              pitch_content = content[start_index:end_index].strip()
              pitch_filename = match.group(1)
              
              # Check if the filename already exists and add a counter if it does
              if pitch_filename in file_counter:
                  file_counter[pitch_filename] += 1
                  output_filename = f"{os.path.splitext(pitch_filename)[0]}_{file_counter[pitch_filename]}.txt"  # Add counter to the filename
              else:
                  file_counter[pitch_filename] = 1
                  output_filename = pitch_filename
              
              output_path = os.path.join(output_folder, output_filename)
              with open(output_path, 'w', encoding='utf-8') as outfile:
                  outfile.write(pitch_content)
              print(f"Created {output_filename}")

if __name__ == "__main__":
    input_folder = r"C:\Users\adhil\OneDrive\Documents\letsgetmoving-project\task-2\new_gemiin_delimiter"  # Replace with the path to your input folder
    output_folder = r"C:\Users\adhil\OneDrive\Documents\letsgetmoving-project\task-2\experiment_out"  # Replace with the path to your output folder
    split_pitch_files(input_folder, output_folder)




import os
import re

def split_pitch_files(input_folder, output_folder):
    """
    Splits pitch files into individual pitch files and names them numerically.

    Args:
        input_folder (str): Path to the folder containing the input files.
        output_folder (str): Path to the folder where output files will be created.
    """

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    pitch_counter = 1  # Initialize counter for all the files

    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_folder, filename)
            with open(input_path, 'r', encoding='utf-8') as infile:
                content = infile.read()

            # Regex to match the start of a pitch text file
            pitch_separator = re.compile(r"^(SharkTankS\d+E\d+_pitch_\d+\.txt)", re.MULTILINE)
            
            # Find the start of each pitch using the regex
            matches = list(pitch_separator.finditer(content))
            
            if not matches:
                print(f"No pitch markers found in {filename}, skipping.")
                continue
                
            # Loop through matches and extract content
            for i, match in enumerate(matches):
              start_index = match.start()
              
              if i+1 < len(matches):
                end_index = matches[i+1].start()
              else:
                  end_index = len(content)

              pitch_content = content[start_index:end_index].strip()
              output_filename = f"pitch_{pitch_counter}.txt"
              output_path = os.path.join(output_folder, output_filename)
              
              with open(output_path, 'w', encoding='utf-8') as outfile:
                  outfile.write(pitch_content)
              print(f"Created {output_filename}")
              pitch_counter += 1 # increment the file counter

if __name__ == "__main__":
    input_folder = r"C:\Users\adhil\OneDrive\Documents\letsgetmoving-project\task-2\new_gemiin_delimiter"  # Replace with the path to your input folder
    output_folder = r"C:\Users\adhil\OneDrive\Documents\letsgetmoving-project\task-2\experiment_out"  # Replace with the path to your output folder
    split_pitch_files(input_folder, output_folder)