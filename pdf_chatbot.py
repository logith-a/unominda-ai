import fitz  # PyMuPDF
import os
from google import genai

# Initialize Gemini client with your API key
client = genai.Client(api_key="AIzaSyBqpVmkAu5R5hC2-RwUYse0Umyby87UFuE")

print("="*60)
print("📚 PDF CHATBOT - Using Gemini AI")
print("="*60)

# -------- STEP 1: LOAD PDFs --------
pdf_folder = "pdfs"
all_text = ""
pages_data = []  # Store info about each page

print(f"\n📂 Looking for PDFs in: {pdf_folder}")

# Check if folder exists
if not os.path.exists(pdf_folder):
    print(f"❌ Folder '{pdf_folder}' not found!")
    print(f"📁 Creating folder '{pdf_folder}'...")
    os.makedirs(pdf_folder)
    print(f"✅ Folder created. Please add PDF files to '{pdf_folder}' and run again.")
    exit()

# Load all PDF files
pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]

if not pdf_files:
    print(f"❌ No PDF files found in '{pdf_folder}' folder!")
    print(f"📁 Please add some PDF files to '{pdf_folder}' and run again.")
    exit()

print(f"\n📄 Found {len(pdf_files)} PDF file(s):")
for pdf_file in pdf_files:
    print(f"   - {pdf_file}")

print("\n🔄 Extracting text from PDFs...")

for file in pdf_files:
    path = os.path.join(pdf_folder, file)
    doc = fitz.open(path)
    
    print(f"   Processing: {file} ({len(doc)} pages)")
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_text = page.get_text()
        
        # Store page info
        pages_data.append({
            "file": file,
            "page": page_num + 1,
            "text": page_text
        })
        
        all_text += page_text + "\n"

print(f"✅ Loaded {len(pages_data)} pages successfully!")
print(f"📊 Total text length: {len(all_text)} characters")

# -------- STEP 2: SIMPLE SEARCH FUNCTION (fallback) --------
def simple_search(question, lines):
    """Simple keyword search as fallback"""
    question_lower = question.lower()
    
    for i, line in enumerate(lines):
        if question_lower in line.lower():
            result = []
            # Show this line + next 5 lines
            for j in range(i, min(i + 6, len(lines))):
                if lines[j].strip():
                    result.append(lines[j])
            return "\n".join(result)
    return None

# -------- STEP 3: CHAT LOOP WITH GEMINI --------
print("\n" + "="*60)
print("🤖 Chatbot is ready! Ask questions about your PDFs")
print("="*60)
print("Type 'exit' to quit")
print("Type 'search' to use simple keyword search instead of AI")
print("-"*60)

# Split text into lines for simple search
lines = all_text.split("\n")
use_simple_search = False

while True:
    print()  # Empty line for spacing
    question = input("📝 Your question: ")
    
    if question.lower() == "exit":
        print("👋 Goodbye!")
        break
    
    if question.lower() == "search":
        use_simple_search = not use_simple_search
        mode = "SIMPLE SEARCH" if use_simple_search else "GEMINI AI"
        print(f"✅ Switched to {mode} mode")
        continue
    
    if not question.strip():
        print("❌ Please enter a question")
        continue
    
    # -------- SIMPLE SEARCH MODE --------
    if use_simple_search:
        print("\n🔍 Searching...")
        answer = simple_search(question, lines)
        
        if answer:
            print("\n📖 Found answer:\n")
            print(answer)
        else:
            print("\n❌ No relevant answer found")
    
    # -------- GEMINI AI MODE --------
    else:
        print("\n🤔 Thinking...")
        
        try:
            # Prepare context (limit to avoid token limits)
            # Use first 5000 characters of each relevant page or all text if small
            if len(all_text) > 10000:
                # Try to find relevant pages (simple keyword matching)
                question_words = set(question.lower().split())
                relevant_pages = []
                
                for page in pages_data:
                    page_lower = page["text"].lower()
                    matches = sum(1 for word in question_words if len(word) > 3 and word in page_lower)
                    if matches > 0:
                        relevant_pages.append((matches, page))
                
                # Sort by relevance
                relevant_pages.sort(reverse=True)
                
                # Take top 3 most relevant pages
                context = ""
                for matches, page in relevant_pages[:3]:
                    context += f"\n--- From {page['file']}, Page {page['page']} ---\n"
                    context += page["text"][:2000] + "\n"  # Limit each page
            else:
                context = all_text
            
            # Create prompt for Gemini
            prompt = f"""You are a helpful assistant that answers questions based ONLY on the provided PDF document content.

DOCUMENT CONTENT:
{context[:15000]}  # Limit total context

QUESTION: {question}

INSTRUCTIONS:
- Answer based ONLY on the document content above
- If the answer isn't in the documents, say "I couldn't find information about that in the PDFs."
- Be concise but include specific details when available
- If possible, mention which document/page the information comes from

ANSWER:"""

            # Get response from Gemini
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            
            print("\n🤖 Answer:\n")
            print(response.text)
            
        except Exception as e:
            print(f"\n❌ Error with Gemini: {e}")
            print("Falling back to simple search...")
            
            # Fallback to simple search
            answer = simple_search(question, lines)
            if answer:
                print("\n📖 Found answer (simple search):\n")
                print(answer)
            else:
                print("\n❌ No relevant answer found")