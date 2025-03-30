import os
import json
import google.generativeai as genai
import re
import sys


# Set your API key
GOOGLE_API_KEY = "AIzaSyBZpusFDGnAW40XG_B3hlT8jR4kzt0fNXA"
genai.configure(api_key=GOOGLE_API_KEY)

# Load the Gemini Pro model
model = genai.GenerativeModel('gemini-2.0-flash')

SYSTEM_PROMPT = """
Role: You are an expert analyst of investor-entrepreneur interactions on TV shows like Shark Tank or Dragon's Den. Your task is to meticulously analyze the questions asked by the investors (Sharks/Dragons) during a business pitch.

Context: You will be provided with the script of a business pitch and the subsequent Q&A session from a show like Shark Tank or Dragon's Den. Your focus is ONLY on the questions asked BY THE INVESTORS.

Action: Carefully review the conversation. For each question asked by an investor, identify the primary business attribute or area of concern that the question addresses. Select the most relevant category from the comprehensive list provided below. Note that a single question might touch on multiple areas, but you should choose the primary intent of the question.

Structure your response as follows:

Investor (e.g., "Mark Cuban"):

Question: [Exact text of the question]

Primary Category: [Select one category from the list below]

Repeat this format for each question asked by each investor. If a single investor asks multiple questions, list them separately.

Question Categories:

1. Business Fundamentals & Viability:

Business Model: Questions about how the business makes money, revenue streams, pricing strategies, cost structure.

Target Market: Questions about the ideal customer, market size, market segmentation, and understanding of customer needs.

Competition: Questions about competitors, competitive advantages, market share, and barriers to entry.

Differentiation/Unique Selling Proposition (USP): Questions exploring what makes the business stand out from the competition.

Scalability: Questions about the ability to grow the business efficiently and handle increased demand.

Sustainability/Long-Term Vision: Questions about the long-term plans for the business, its ability to adapt to market changes, and its overall vision.

Operations: Questions about the day-to-day running of the business, manufacturing, logistics, and supply chain.

Legal/Regulatory: Questions about patents, trademarks, compliance, and legal risks.

Market Traction: Questions about customer acquisition, sales, and evidence of demand.

Distribution Channels: How the product/service reaches the customer.

2. Financial Performance & Valuation:

Revenue: Questions about current and projected revenue, sales growth, and revenue sources.

Profitability: Questions about profit margins, cost of goods sold, operating expenses, and net profit.

Valuation: Questions about the company's worth, justification for the valuation, and comparable company data.

Financial Projections: Questions about the assumptions behind financial forecasts and the realism of those projections.

Funding/Investment History: Questions about previous funding rounds, use of funds, and current capital structure.

Burn Rate/Cash Flow: Questions about how quickly the company is spending money and its ability to manage cash flow.

Customer Acquisition Cost (CAC): How much it costs to gain a customer.

Lifetime Value of a Customer (LTV): The predicted revenue a customer will generate during their relationship with the company.

3. Product/Service Attributes:

Functionality/Features: Questions about the product's capabilities and specific features.

Innovation/Technology: Questions about the novelty of the product or service, its technology, and intellectual property.

Product Development: Questions about the stage of development, future product roadmap, and development costs.

Manufacturing/Production: Questions related to how the product is made.

Intellectual Property: Questions about patents, trademarks, and other protections.

Usability/User Experience: How easy and enjoyable the product/service is to use.

Quality: Standards and measures taken to ensure the product/service meets expectations.

4. Team & Leadership:

Experience/Expertise: Questions about the team's background, skills, and relevant experience.

Leadership/Management: Questions about the leadership team's vision, strategy, and ability to execute.

Team Dynamics: Questions about the team's relationships, roles, and responsibilities.

Founder Commitment/Motivation: Questions to understand the founders' drive and dedication.

Advisory Board/Mentors: Who is advising the team.

5. Investment & Deal Terms:

Use of Funds: Questions about how the investment will be used to grow the business.

Equity/Ownership: Questions about the percentage of ownership being offered and the existing equity structure.

Exit Strategy: Questions about the potential for a future sale or IPO.

Return on Investment (ROI): Questions to understand the potential return for the investors.

Control/Influence: Questions about the investor's role in the company's decision-making.

6. Market Position & Strategy:

Marketing & Sales Strategy: Questions about how the company plans to reach its target market and generate sales.

Customer Acquisition: Questions about strategies and tactics used to acquire new customers.

Brand Awareness: Questions about building recognition and reputation for the brand.

Pricing Strategy: Questions about the company's approach to setting prices.

Market Trends: How the business is aligned with current trends.

7. Risks & Challenges:

Potential Risks: Questions about potential threats to the business, such as competition, regulatory changes, or economic downturns.

Contingency Plans: Questions about how the company plans to address potential challenges.

Barriers to Entry: Obstacles that prevent new competitors from easily entering the market.

8. Impact & Sustainability:

Social Impact: The business's positive effect on society.

Environmental Impact: The business's effect on the environment.

Ethical Considerations: Questions about the company's adherence to ethical standards.

Example:

Investor: Kevin O'Leary

Question: "What are your gross margins on each unit?"

Primary Category: Profitability

OUTPUT FORMAT:
Provide a JSON object containing the extracted information for each business pitch.
For each investor question, include the investor's name, the exact question asked, and the primary category it falls under.  If an attribute is not mentioned in the transcript, leave it as "not_provided".
For example:

{
  "questions": [
    {
      "Investor": "Mark Cuban",
      "Question": "How do you acquire new customers?",
      "Primary Category": "Customer Acquisition"
    },
    {
      "Investor": "Kevin O'Leary",
      "Question": "What are your gross margins on each unit?",
      "Primary Category": "Profitability"
    },
    {
      "Investor": "Lori Greiner",
      "Question": "Do you have any patents?",
      "Primary Category": "Intellectual Property"
    }
  ]
}
"""


def clean_transcript(transcript):
    # Remove non-printable characters
    transcript = ''.join(c for c in transcript if c.isprintable())
    # Replace problematic characters (example)
    transcript = transcript.replace("’", "'")  # Replace curly apostrophes
    transcript = re.sub(r"[\x00-\x1F\x7F-\xFF]", "", transcript)  # remove control characters and extended ascii
    return transcript

def fix_json(json_string):
    # Remove trailing commas (more robust)
    json_string = re.sub(r",(\s*?[\}\]])", r"\1", json_string)
    return json_string

try:
    import jsonrepair
    def repair_json(json_string):
        try:
            repaired_json_string = jsonrepair.repair_json(json_string)
            return repaired_json_string
        except:
            return None # or raise the exception if you want to know it failed
except ImportError:
    print("Please install jsonrepair package to use repair_json functionality")


def process_pitch(filepath, output_dir):
    """Processes a single pitch file and saves the output JSON."""
    print(f"Starting processing file: {filepath}")  # Indicate file processing start
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Load the JSON data from the input file
            data = json.load(f)

            # Extract questions and investor names
            questions_data = []
            if 'pitches' in data and len(data['pitches']) > 0 and 'questions' in data['pitches'][0]:
                for question_data in data['pitches'][0]['questions']:
                    investor = question_data.get('speaker', 'Unknown Investor')
                    question = question_data.get('raw_text', '')
                    if investor != 'Entrepreneur':  # Only consider investor questions
                        questions_data.append(f"Investor: {investor}\nQuestion: {question}\n")

            transcript = "\n".join(questions_data)

            if not transcript:
                print(f"Error: No questions/responses found in JSON file: {filepath}")
                return

    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file {filepath}: {e}")
        return
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return

    try:
        # Clean the transcript *before* sending it to the LLM
        transcript = clean_transcript(transcript)

        # Send the transcript and system prompt to the Gemini model
        response = model.generate_content([SYSTEM_PROMPT, transcript])
        response_text = response.text

        # Clean up response text to handle potential markdown
        if response_text.startswith("```json"):
            response_text = response_text[len("```json"):]
        if response_text.endswith("```"):
            response_text = response_text[:-len("```")]
        response_text = response_text.strip() # Remove leading/trailing whitespace

        # Debugging: Print the cleaned response text *before* attempting to load it as JSON
        print("Cleaned Response Text (before fixing):\n", response_text)  # <---- ADDED

        # Try to fix the JSON *before* parsing
        response_text = fix_json(response_text) #Apply simple regex fixes
        if 'jsonrepair' in sys.modules:
            repaired_json = repair_json(response_text) #Try more complex repair
            if repaired_json:
                response_text = repaired_json
                print("JSON was repaired using jsonrepair")
            else:
                print("JSON repair with jsonrepair failed")


        # Extract the JSON from the response.
        try:
            json_output = json.loads(response_text)
            print("JSON loaded successfully!") #debug
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e}")
            print(f"Raw Response text: {response.text}") # Print the original raw response
            print(f"Cleaned Response text: {response_text}") # Print the cleaned text for inspection

            # NEW: Print a snippet of the text around the error location
            #error_line = 802  # Approximate line number from the error  (You may not know the line number now)
            #start_char = max(0, 31584 - 200)  # Show 200 characters before...
            #end_char = 31584 + 200              # ...and 200 characters after
            #print(f"Snippet around error (char 31584):\n", response_text[start_char:end_char])

            #Instead of snippet around specific character print the first 500 characters
            print(f"First 500 characters of JSON for debugging:\n", response_text[:500])

            # Handle the error gracefully:
            # 1. Log the error and the original/fixed JSON
            # 2. Return a default JSON structure with error flags
            # 2. Retry with a simplified prompt, etc.
            return

        # Save the JSON output to a file
        filename = os.path.basename(filepath).replace('.json', '_output.json') # Changed extension
        output_path = os.path.join(output_dir, filename)

        with open(output_path, 'w', encoding='utf-8') as outfile:
            json.dump(json_output, outfile, indent=4)

        print(f"Processed {filepath} and saved output to {output_path}")

    except Exception as e:
        print(f"Error processing {filepath}: {e}")



def process_directory(input_dir, output_dir):
    """Processes all pitch files in a directory, skipping already processed ones."""

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    json_files = [filename for filename in os.listdir(input_dir) if filename.endswith('.json')] # Changed extension
    total_files = len(json_files)
    print(f"Total .json files found in input directory: {total_files}")

    processed_count = 0
    skipped_count = 0

    for index, filename in enumerate(json_files):
        filepath = os.path.join(input_dir, filename)
        output_filename = os.path.basename(filepath).replace('.json', '_output.json') # Changed extension
        output_path = os.path.join(output_dir, output_filename)

        if os.path.exists(output_path):
            print(f"Skipping file {index + 1} of {total_files}: {filename} (already processed)")
            skipped_count += 1
            continue

        print(f"Processing file {index + 1} of {total_files}: {filename}") # Indicate file number and name
        process_pitch(filepath, output_dir)
        processed_count +=1

    print(f"Processing complete.  Processed {processed_count} files, skipped {skipped_count} files.")


# Example Usage:
input_directory = r"C:\Users\adhil\OneDrive\Documents\letsgetmoving-project\task-2\gemini_2oflash json output"  # Replace with your input directory
output_directory = r"C:\Users\adhil\OneDrive\Documents\letsgetmoving-project\task-2\Question_extraction\gemini_2.0"  # Replace with your desired output directory

process_directory(input_directory, output_directory)
print("Processing complete.")