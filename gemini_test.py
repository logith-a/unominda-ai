import google.generativeai as genai

# STEP 1: Paste your API key here
genai.configure(api_key="AIzaSyDn6o-jAmGdMMVIhxt7c2SFT-64_OCB-W8")

# STEP 2: Choose model
model = genai.GenerativeModel("gemini-1.5-flash")

# STEP 3: Ask something
response = model.generate_content("Explain what AI is in simple words")

print(response.text)