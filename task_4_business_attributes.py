import os
import json
import google.generativeai as genai
import re
import sys


# Set your API key
GOOGLE_API_KEY = "AIzaSyDcQfNWwD2hk3IObZpSTuhqbO46ctg6YoU"
genai.configure(api_key=GOOGLE_API_KEY)

# Load the Gemini Pro model
model = genai.GenerativeModel('gemini-2.0-flash')

SYSTEM_PROMPT = """
Role: You are an expert in extracting relevant and structured information from investor/entrepreneur interactions in TV shows like Shark Tank or Dragon's Den.

Context: I am providing you with the script of an entire pitch and Q&A for a business featured on a reality TV show Shark Tank or Dragon’s Den.

Action: Carefully review the conversation between the entrepreneur(s) and the investors. Based on the script, identify and extract the following **business identifiers**: `business_name`, `business_id`, `pitch_id`, and `business_founders`. If any of these identifiers are not explicitly mentioned in the transcript, please mark them as "not_provided".

After extracting the business identifiers, proceed to extract information based on the exhaustive list of business attributes provided below.
If an attribute is not directly discussed in the conversation, leave it empty. Please select your answer from the provided options for each category.
Structure your response in a clear and organized manner, presenting the extracted information for the business identifiers at the top level, followed by the extracted information for each business attribute within the "Business Attributes" section.

BUSINESS ATTRIBUTES:

1. Business Fundamentals
    Business Origin Story
        Inspiration Source: [Personal Problem/Need, Market Gap Identification, Scientific/Academic Research, Industry Experience, Family Business Evolution, Hobby Turned Business, Social/Environmental Issue, Cultural Heritage/Tradition, Technological Innovation, Market Trend Response, Accidental Discovery, Customer Request/Feedback, Competition Inadequacy, Regulatory Change Response, Crisis/Pandemic Response, Professional Experience]
        Development Timeline: [Sudden Inspiration, Gradual Evolution, Pivoted from Different Concept, Research-Based Development, Customer Co-Creation, Accelerator/Incubator Program, Corporate Spin-off, Academic Project Extension, Side Project Evolution, Emergency Response, Planned Launch, Opportunity-Driven, Market-Driven Timing, Season/Event-Specific, Crisis-Driven, Trend-Following]
    Regulatory Requirements
        Compliance Status: [Fully Compliant, In Process, Pending Approval, Exempt, Not Yet Started]
        Specific Compliance: [International Compliance, State/Local Compliance, Industry-Specific Compliance, Patent Compliance, Environmental Compliance, Health & Safety Compliance, Data Privacy Compliance, Financial Compliance, Import/Export Compliance, Manufacturing Compliance, Professional Licensing]
        Regulatory Bodies: [FDA, EPA, FCC, USDA, SEC, CPSC, DOT, OSHA, State Agencies, Local Authorities, International Regulators, Industry Associations, Professional Boards, Testing Laboratories, Certification Bodies, Standards Organizations]
    Market Recognition
        Achievements & Awards: [Industry Awards, Innovation Recognition, Environmental Awards, Design Awards, Customer Choice Awards, Business Growth Awards, Entrepreneur Awards, Local Business Awards, International Recognition, Media Coverage, Celebrity Endorsements, Expert Recommendations, Competition Wins, Patent Awards, Research Recognition, Social Impact Awards]
        Public Perception: [Trendsetter, Industry Leader, Innovation Pioneer, Social Impact Leader, Controversial, Traditional/Conservative, Luxury/Premium, Value-Focused, Tech-Forward, Environmentally Conscious, Customer-Centric, Quality Leader, Disruptor, Community Favorite, Expert Choice, Mass Market Appeal]
    Industry Classification
        Primary Industry: [Technology & Digital, Consumer Goods & Retail, Food & Beverage, Healthcare & Wellness, Fashion & Apparel, Education & Training, Entertainment & Media, Professional Services, Manufacturing & Industrial, Real Estate & Construction, Transportation & Logistics, Agriculture & Farming, Energy & Sustainability, Sports & Recreation, Beauty & Personal Care, Home & Garden, Pets & Animal Care, Financial Services & Insurance, Travel & Hospitality, Arts & Crafts]
        Sub-Industry Examples: [Software Development & SaaS, Mobile Applications, Artificial Intelligence & Machine Learning, Internet of Things (IoT), Cloud Services, Cybersecurity, Gaming & Interactive Entertainment, Educational Technology, Financial Technology, Health Technology, Blockchain & Cryptocurrency, Robotics & Automation, Data Analytics & Business Intelligence, Virtual/Augmented Reality, E-commerce Platforms, Digital Marketing Tools, Artisanal & Specialty Foods, Ready-to-Eat Meals, Beverages & Drinks, Health & Nutrition, Snacks & Confectionery, Restaurant Concepts, Food Technology, Meal Delivery Services, Plant-Based & Alternative Foods, Brewing & Spirits, Organic & Natural Foods, Food Safety & Processing, Catering & Events, Dietary Supplements, Agricultural Technology, Food Waste Solutions, etc.]
    Development Stage: [Concept/Idea Only, Early Research & Development, Prototype Development, Beta Testing/Market Testing, Minimum Viable Product (MVP), Initial Market Launch, Revenue Generating, Growth Phase, Scaling Operations, Established Business, Expansion Phase, International Operations, Turnaround/Restructuring, Pre-Exit Stage, Franchise Development, Mature/Stable Operations]
    Business Model
        Primary Revenue Model: [Direct Sales (One-time Purchase), Subscription Services, Freemium Model, Marketplace/Platform, Licensing & Royalties, Franchise Operations, Advertisement-Based, Service-Based, Hardware + Software Combined, Usage-Based Pricing, Commission-Based, Hybrid Model, Pay-Per-Use, White Label/Private Label, Rental/Leasing, Value-Added Reseller]
        Target Market Segment: [Business-to-Business (B2B), Business-to-Consumer (B2C), Business-to-Government (B2G), Consumer-to-Consumer (C2C), Business-to-Business-to-Consumer (B2B2C), Direct-to-Consumer (D2C), Mixed/Hybrid Approach]

2. Financial Metrics
    Revenue Brackets (Annual): [Pre-Revenue, Under $50,000, $50,000 - $100,000, $100,000 - $250,000, $250,000 - $500,000, $500,000 - $1 million, $1 million - $5 million, $5 million - $10 million, $10 million - $25 million, $25 million - $50 million, $50 million - $100 million, Over $100 million]
    Profitability Status: [Pre-Profit Stage, Break-Even Point Reached, Early Profitability, Consistently Profitable, High-Margin Operations (>30%), Declining Profitability, Variable Profitability, Loss-Making but Growing, Loss-Making with Clear Path to Profitability, Profitable with Reinvestment Focus, Mature Profit Stage, Cash Flow Positive]
    Cost Structure Components: [Raw Materials & Supplies, Manufacturing & Production, Labor & Workforce, Technology Infrastructure, Marketing & Advertising, Research & Development, Intellectual Property & Licensing, Distribution & Logistics, Customer Service & Support, Administrative & Overhead, Facilities & Equipment, Sales & Commission, Professional Services, Quality Control, Training & Development, Regulatory Compliance]
    Investment Profile
        Previous Funding Sources: [Bootstrap Only, Friends & Family, Angel Investors, Seed Funding, Venture Capital, Private Equity, Crowdfunding, Bank Loans, Government Grants, Strategic Investors, Corporate Investment, Initial Public Offering (IPO), Revenue-Based Financing, Equipment Financing, Convertible Notes, SAFE Notes]
        Investment Ask: [Under $50,000, $50,000 - $250,000, $250,000 - $500,000, $500,000 - $1 million, $1 million - $5 million, $5 million - $10 million, Over $10 million]
        Equity Offered: [Under 5%, 5-10%, 11-15%, 16-20%, 21-25%, 26-30%, 31-40%, Over 40%]

3. Market Position
    Customer Engagement
        Feedback Channels: [Social Media, Customer Service, Focus Groups, Beta Testing, User Reviews, Surveys, Direct Feedback, Community Forums, Advisory Panels, In-Store Feedback, App Reviews, Product Testing, User Research, Customer Interviews, Usage Analytics, Complaint Systems]
        Customer Loyalty Programs: [Points System, Tiered Rewards, Subscription Benefits, VIP Program, Early Access, Exclusive Products, Member Events, Referral Program, Birthday Rewards, Anniversary Benefits, Community Access, Educational Content, Premium Support, Partner Benefits, Customized Rewards, Social Impact Rewards]
    Digital Presence
        Online Platforms: [Company Website, Mobile App, Social Media Presence, E-commerce Platform, Online Marketplace, Content Platform, Community Platform, Educational Platform, Service Platform, Booking System, Customer Portal, Partner Portal, API Integration, Virtual Showroom, Digital Catalog, Support Platform]
        Digital Marketing Channels: [Search Engine Marketing, Social Media Marketing, Email Marketing, Content Marketing, Influencer Marketing, Affiliate Marketing, Video Marketing, Display Advertising, Native Advertising, Podcast Advertising, Mobile Marketing, Programmatic Advertising, Retargeting, Partnership Marketing, Community Marketing, Viral Marketing]
    Market Size Categories: [Micro Market (<$1M), Small Market ($1M-$10M), Medium Market ($10M-$100M), Large Market ($100M-$1B), Very Large Market ($1B-$10B), Massive Market (>$10B)]
    Competition Level: [No Direct Competition, Limited Competition (1-3 competitors), Moderate Competition (4-10 competitors), High Competition (10+ competitors), Dominated Market (Few large players), Fragmented Market (Many small players), Emerging Market (New category), Saturated Market, Consolidating Market, Disrupted Market]
    Competitive Position: [Market Leader, Strong Challenger, Niche Player, New Entrant, Disruptor, Fast Follower, Premium Provider, Cost Leader, Innovation Leader, Quality Leader, Service Leader, Specialized Provider]

4. Product/Service Attributes
    Innovation Level: [Revolutionary (New to World), Significant Improvement, Moderate Innovation, Minor Enhancement, Me-Too Product, Category Creator, Market Transformer, Process Innovation, Business Model Innovation, Technology Innovation, Design Innovation, Service Innovation]
    Intellectual Property Status: [Patent Pending, Granted Patents, Provisional Patents, Trade Secrets, Copyrights, Trademarks, Design Patents, Licensing Rights, No Protection, Patent Portfolio, International Patents, Industry Standards]
    Development Status: [Conceptual Phase, Research Phase, Design Phase, Prototype Phase, Alpha Testing, Beta Testing, Market Testing, Production Ready, Scaling Production, Multiple Generations, Continuous Innovation, Legacy Product, Next Generation Development, Custom Development, Mass Production, Limited Production]

5. Team Composition
    Leadership Experience: [First-Time Entrepreneurs, Serial Entrepreneurs, Industry Veterans, Mixed Experience Team]
    Background: [Academic Background, Corporate Background, Technical Experts, Sales Leaders, Operations Experts, Financial Experts, Marketing Professionals, Product Specialists]
    Team Size: [Solo Founder, Co-Founders (2-3), Small Team (4-10), Medium Team (11-50), Large Team (51-200), Enterprise (201-1000), Corporate (1000+)]
    Expertise Coverage: [Technical/Engineering, Business/Management, Marketing/Sales, Operations/Logistics, Finance/Accounting, Industry-Specific, Legal/Regulatory, Product Development, Customer Service, Research/Development, Manufacturing/Production, International Business]

6. Growth & Scalability
    Growth Rate: [Pre-Growth, Early Growth (<20% annual), Moderate Growth (20-50% annual), Fast Growth (50-100% annual), Hypergrowth (>100% annual), Negative Growth, Plateaued Growth, Cyclical Growth, Steady Growth, Accelerating Growth, Declining Growth]
    Scalability Potential: [Highly Scalable, Moderately Scalable, Limited Scalability, Location Dependent, Resource Dependent, Technology Dependent, Market Dependent, Capital Dependent, Team Dependent, Infrastructure Dependent, Regulation Dependent]
    International Potential: [Local Market Only, Regional Expansion Possible, National Expansion Ready, International Expansion Ready, Global Market Potential, Export Ready, Franchise Potential, Licensing Potential, E-commerce Potential, Multi-Market Potential]

7. Impact & Sustainability
    Product Lifecycle Impact
        Manufacturing Impact: [Zero Waste Manufacturing, Energy-Efficient Production, Water Conservation, Renewable Materials, Local Production, Automated Production, Lean Manufacturing, Green Factory, Recycled Materials, Upcycled Materials, Biodegradable Materials, Non-Toxic Processes, Waste Recovery, Energy Recovery, Carbon-Neutral Production, Sustainable Packaging]
        End-of-Life Management: [Recyclable Products, Biodegradable Products, Take-Back Programs, Refurbishment Programs, Upcycling Programs, Waste Management, Component Recovery, Material Recovery, Second-Life Programs, Circular Economy, Product Repurposing, Responsible Disposal, Extended Life Design, Modular Design, Repair Program, Recycling Partnership]
    Community Integration
        Local Impact: [Job Creation Quality, Skills Development, Local Supplier Network, Community Events, Educational Programs, Infrastructure Development, Local Partnerships, Cultural Preservation, Public Space Improvement, Health Initiatives, Youth Programs, Senior Programs, Disability Support, Minority Support, Emergency Support, Economic Development]
        Global Responsibility: [Fair Trade Practices, Indigenous Rights, Cultural Sensitivity, Global Health Impact, Education Access, Technology Transfer, Knowledge Sharing, Capacity Building, Disaster Response, Refugee Support, Cross-Cultural Exchange, International Development, Global Standards, Universal Access, Democratic Practices, Human Rights]
    Environmental Impact: [Net Positive Impact, Carbon Neutral, Minimal Environmental Impact, Moderate Environmental Impact, High Environmental Impact, Impact Reduction Plan, Circular Economy Model, Waste Reduction Focus, Energy Efficiency Focus, Resource Conservation, Environmental Innovation, Sustainability Leader]
    Social Impact: [Job Creation, Community Development, Education/Skills Development, Health Improvement, Social Inclusion, Cultural Preservation, Poverty Reduction, Gender Equality, Accessibility Improvement, Youth Empowerment, Elder Care, Disability Support]
    Sustainability Practices: [Sustainable Materials, Renewable Energy Use, Waste Reduction, Circular Economy, Fair Trade, Ethical Supply Chain, Local Sourcing, Water Conservation, Biodiversity Protection, Carbon Offsetting, Green Manufacturing, Sustainable Packaging]

8. Risk Assessment
    Operational Risks: [Supply Chain Dependency, Manufacturing Complexity, Quality Control Issues, Staffing Challenges, Technology Risks, Regulatory Compliance, Market Access, Scale-up Challenges, Customer Service Delivery, Infrastructure Requirements]
    Market Risks: [Market Acceptance, Competition Level, Price Sensitivity, Market Timing, Technology Changes, Consumer Behavior, Economic Conditions, Regulatory Changes, Geographic Limitations, Industry Disruption]
    Financial Risks: [Capital Requirements, Cash Flow Management, Currency Exposure, Credit Risk, Investment Requirements, Operating Costs, Pricing Pressure, Revenue Stability, Funding Availability, Exit Opportunities]

9. Exit Strategy
    Planned Exit Options: [Initial Public Offering (IPO), Strategic Acquisition, Private Equity Sale, Management Buyout, Family Succession, Licensing Deal, Franchise Development, Merger, Employee Stock Ownership Plan, Long-term Private Ownership]
    Exit Timeline: [Short-term (1-3 years), Medium-term (3-5 years), Long-term (5-10 years), No Specific Timeline, Event-Dependent, Market-Dependent, Growth-Dependent, Opportunity-Dependent]

10. Innovation & Research
    Research & Development
        R&D Focus Areas: [Product Innovation, Process Innovation, Material Innovation, Technology Innovation, User Experience, Sustainability, Cost Reduction, Quality Improvement, Safety Enhancement, Efficiency Improvement, Performance Optimization, Design Innovation, Service Innovation, Business Model Innovation, Market Innovation, Social Innovation]
        Research Partnerships: [University Collaboration, Industry Partnership, Government Research, Private Research Labs, International Collaboration, Startup Collaboration, Corporate Partnership, Research Consortium, Innovation Hub, Technology Transfer, Clinical Trials, Field Research, Consumer Research, Market Research, Scientific Research, Applied Research]
    Technology Integration
        Core Technologies: [Artificial Intelligence, Machine Learning, Blockchain, Internet of Things, Cloud Computing, Edge Computing, 5G/6G, Quantum Computing, Robotics, Automation, Virtual Reality, Augmented Reality, Big Data Analytics, Natural Language Processing, Computer Vision, Biotechnology]
        Technology Implementation: [In-House Development, Licensed Technology, Open Source, Proprietary Systems, Hybrid Solutions, Custom Development, Platform Integration, API Development, Mobile Integration, Cloud Migration, Legacy Integration, Security Implementation, Data Management, Network Infrastructure, Hardware Integration, Software Development]

11. Customer Experience
    Service Delivery
        Service Channels: [Physical Store, Online Platform, Mobile App, Phone Support, Email Support, Chat Support, Video Support, Self-Service Portal, Community Support, Social Media Support, In-Person Service, Remote Service, Hybrid Service, VR/AR Service, AI-Powered Support, Human-Assisted AI]
        Customer Journey: [Awareness Phase, Consideration Phase, Purchase Decision, Onboarding Process, Usage Period, Support Experience, Feedback Collection, Loyalty Building, Referral Process, Renewal Process, Upgrade Path, Cross-Sell/Upsell, Win-Back Process, Exit Process, Post-Service Follow-up, Lifetime Relationship]
    Personalization Capabilities
        Data Collection: [Data Collection, Purchase History, Browsing Behavior, Service Usage, Feedback Data, Social Media Data, Location Data, Device Data, Demographic Data, Preference Data, Interaction Data, Survey Responses, Customer Service Data, Product Usage Data, Payment Behavior, Return History, Review Content]
        Customization Options: [Product Customization, Service Personalization, Communication Preferences, Interface Customization, Pricing Options, Delivery Options, Payment Options, Support Options, Language Options, Accessibility Options, Content Personalization, Recommendation Engine, Custom Solutions, Personalized Offers, Custom Packaging, Experience Customization]

12. Additional Considerations
    Cultural Fit: [Innovation Focus, Sustainability Focus, Social Impact Focus, Technology Focus, Traditional Business Values, Growth Mindset, Customer-Centric, Quality-Focused, Community-Focused, Global Perspective]
    Marketing Strategy: [Digital Marketing, Traditional Advertising, Content Marketing, Social Media Focus, Influencer Marketing, Direct Marketing, Event Marketing, Public Relations, Word-of-Mouth, Partnership Marketing, Brand Development, Community Building]
    Customer Relationship: [Transaction-Based, Relationship-Based, Community-Based, Subscription-Based, Service-Based, Consultation-Based, Education-Based, Solution-Based, Experience-Based, Value-Based]

OUTPUT FORMAT:
Provide a JSON object containing the extracted information for each business pitch.
The JSON object should have the following top-level keys: `business_name`, `business_id`, `pitch_id`, `business_founders`, and `Business Attributes`.
For `business_name`, `business_id`, `pitch_id`, and `business_founders`, extract the information directly from the transcript if available, otherwise, set the value to "not_provided".
For the `Business Attributes`, select the most appropriate value from the provided options for each attribute. If an attribute is not mentioned in the transcript, leave it as "not_provided".

For example:

{
  "business_name": "Example Business Name",
  "business_id": "business123",
  "pitch_id": "pitch456",
  "business_founders": ["Founder Name 1", "Founder Name 2"],
  "Business Attributes": {
    "Business Fundamentals": {
      "Business Origin Story": {
        "Inspiration Source": "Personal Problem/Need",
        "Development Timeline": "Gradual Evolution"
      },
      "Regulatory Requirements": {
        "Compliance Status": "Fully Compliant",
        "Specific Compliance": "State/Local Compliance",
        "Regulatory Bodies": "State Agencies"
      },
      "Market Recognition": {
        "Achievements & Awards": "Customer Choice Awards",
        "Public Perception": "Value-Focused"
      },
      "Industry Classification": {
        "Primary Industry": "Consumer Goods & Retail",
        "Sub-Industry Examples": "E-commerce Platforms"
      },
      "Development Stage": "Revenue Generating",
      "Business Model": {
        "Primary Revenue Model": "Direct Sales (One-time Purchase)",
        "Target Market Segment": "Business-to-Consumer (B2C)"
      }
    },
    "Financial Metrics": {
      "Revenue Brackets (Annual)": "$100,000 - $250,000",
      "Profitability Status": "Early Profitability",
      "Cost Structure Components": "Marketing & Advertising",
      "Investment Profile": {
        "Previous Funding Sources": "Friends & Family",
        "Investment Ask": "$50,000 - $250,000",
        "Equity Offered": "11-15%"
      }
    },
    "Market Position": {
      "Customer Engagement": {
        "Feedback Channels": "Social Media",
        "Customer Loyalty Programs": "Points System"
      },
      "Digital Presence": {
        "Online Platforms": "Company Website",
        "Digital Marketing Channels": "Social Media Marketing"
      },
      "Market Size Categories": "Small Market ($1M-$10M)",
      "Competition Level": "Moderate Competition (4-10 competitors)",
      "Competitive Position": "Niche Player"
    },
    "Product/Service Attributes": {
      "Innovation Level": "Significant Improvement",
      "Intellectual Property Status": "Trademarks",
      "Development Status": "Production Ready"
    },
    "Team Composition": {
      "Leadership Experience": "First-Time Entrepreneurs",
      "Background": "Marketing Professionals",
      "Team Size": "Co-Founders (2-3)",
      "Expertise Coverage": "Marketing/Sales"
    },
    "Growth & Scalability": {
      "Growth Rate": "Moderate Growth (20-50% annual)",
      "Scalability Potential": "Moderately Scalable",
      "International Potential": "Regional Expansion Possible"
    },
    "Impact & Sustainability": {
      "Product Lifecycle Impact": {
        "Manufacturing Impact": "Sustainable Packaging",
        "End-of-Life Management": "Recyclable Products"
      },
      "Community Integration": {
        "Local Impact": "Local Supplier Network",
        "Global Responsibility": "Fair Trade Practices"
      },
      "Environmental Impact": "Minimal Environmental Impact",
      "Social Impact": "Job Creation",
      "Sustainability Practices": "Sustainable Materials"
    },
    "Risk Assessment": {
      "Operational Risks": "Supply Chain Dependency",
      "Market Risks": "Market Acceptance",
      "Financial Risks": "Capital Requirements"
    },
    "Exit Strategy": {
      "Planned Exit Options": "Strategic Acquisition",
      "Exit Timeline": "Medium-term (3-5 years)"
    },
    "Innovation & Research": {
      "Research & Development": {
        "R&D Focus Areas": "Product Innovation",
        "Research Partnerships": "University Collaboration"
      },
      "Technology Integration": {
        "Core Technologies": "Artificial Intelligence",
        "Technology Implementation": "In-House Development"
      }
    },
    "Customer Experience": {
      "Service Delivery": {
        "Service Channels": "Online Platform",
        "Customer Journey": "Usage Period"
      },
      "Personalization Capabilities": {
        "Data Collection": "Purchase History",
        "Customization Options": "Product Customization"
      }
    },
    "Additional Considerations": {
      "Cultural Fit": "Innovation Focus",
      "Marketing Strategy": "Digital Marketing",
      "Customer Relationship": "Transaction-Based"
    }
  }
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

            # Extract and combine questions and responses
            transcript = ""
            if 'pitches' in data and len(data['pitches']) > 0 and 'questions' in data['pitches'][0]:
                for question_data in data['pitches'][0]['questions']:
                    transcript += f"Question: {question_data.get('raw_text', '')}\n"
                    transcript += f"Response: {question_data.get('response_text', '')}\n"
                    transcript += "\n"  # Add a separator between Q&A pairs

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
            # 3. Retry with a simplified prompt, etc.
            return

        # Save the JSON output to a file
        filename = os.path.basename(filepath).replace('.json', '_output.json') # Changed extension
        output_path = os.path.join(output_dir, filename)

        with open(output_path, 'w', encoding='utf-8') as outfile:
            json.dump(json_output, outfile, indent=4, ensure_ascii=False) # Added ensure_ascii=False

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
output_directory = r"C:\Users\adhil\OneDrive\Documents\letsgetmoving-project\task-2\Business attribute extraction\new"  # Replace with your desired output directory

process_directory(input_directory, output_directory)
print("Processing complete.")