import fitz  # PyMuPDF
import os
import pytesseract
from PIL import Image
import io
from google import genai

# Configure Tesseract path (update this to your Tesseract installation path)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Initialize Gemini client
client = genai.Client(api_key="AIzaSyBqpVmkAu5R5hC2-RwUYse0Umyby87UFuE")

print("="*70)
print("🤖 FRIENDLY PDF CHATBOT - With OCR + Gemini AI")
print("="*70)

class FriendlyPDFChatbot:
    def __init__(self, pdf_folder="pdfs"):
        self.pdf_folder = pdf_folder
        self.documents = ""
        self.lines = []
        self.pages_data = []  # Store detailed page info
        self.pdf_files = []
        self.pdfs_loaded = False
        
    def extract_text_with_ocr(self, pdf_path):
        """Extract text from PDF using OCR for scanned documents"""
        doc = fitz.open(pdf_path)
        text_content = ""
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Try to extract text normally first
            text = page.get_text()
            
            # If normal extraction yields little text, use OCR
            if len(text.strip()) < 50:  # Threshold for scanned pages
                print(f"   📸 Page {page_num + 1}: Using OCR (scanned page)")
                
                # Convert PDF page to image
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                # Perform OCR
                try:
                    ocr_text = pytesseract.image_to_string(img)
                    text_content += ocr_text + "\n"
                    
                    # Store OCR info
                    self.pages_data.append({
                        "file": os.path.basename(pdf_path),
                        "page": page_num + 1,
                        "text": ocr_text,
                        "method": "OCR"
                    })
                except Exception as e:
                    print(f"   ❌ OCR failed on page {page_num + 1}: {e}")
                    text_content += text + "\n"  # Fallback to normal text
                    self.pages_data.append({
                        "file": os.path.basename(pdf_path),
                        "page": page_num + 1,
                        "text": text,
                        "method": "Normal (fallback)"
                    })
            else:
                print(f"   📄 Page {page_num + 1}: Using normal text extraction")
                text_content += text + "\n"
                self.pages_data.append({
                    "file": os.path.basename(pdf_path),
                    "page": page_num + 1,
                    "text": text,
                    "method": "Normal"
                })
        
        return text_content
    
    def load_pdfs(self):
        """Load all PDFs from the folder"""
        print(f"\n📂 Scanning folder: {self.pdf_folder}")
        
        # Check if folder exists
        if not os.path.exists(self.pdf_folder):
            print(f"❌ Folder '{self.pdf_folder}' not found!")
            print(f"📁 Creating folder '{self.pdf_folder}'...")
            os.makedirs(self.pdf_folder)
            print(f"✅ Folder created. Please add PDF files and run again.")
            return False
        
        # Get all PDF files
        self.pdf_files = [f for f in os.listdir(self.pdf_folder) if f.lower().endswith('.pdf')]
        
        if not self.pdf_files:
            print(f"⚠️  No PDF files found in '{self.pdf_folder}'!")
            print("   You can still chat with me normally, but I won't have any PDFs to reference.")
            self.pdfs_loaded = False
            return True  # Return True so chat can still work
        
        print(f"\n📄 Found {len(self.pdf_files)} PDF file(s):")
        for pdf in self.pdf_files:
            print(f"   - {pdf}")
        
        print("\n🔄 Processing PDFs...")
        
        for file in self.pdf_files:
            path = os.path.join(self.pdf_folder, file)
            print(f"\n📖 Reading: {file}")
            
            # Extract text (with OCR if needed)
            file_text = self.extract_text_with_ocr(path)
            self.documents += f"\n\n----- START OF {file} -----\n\n"
            self.documents += file_text
            self.documents += f"\n\n----- END OF {file} -----\n\n"
        
        # Split into lines for simple search
        self.lines = self.documents.split("\n")
        
        print(f"\n✅ All PDFs processed successfully!")
        print(f"📊 Total pages processed: {len(self.pages_data)}")
        print(f"📊 Total text length: {len(self.documents)} characters")
        
        # Show extraction stats
        normal_count = sum(1 for p in self.pages_data if p["method"] == "Normal")
        ocr_count = sum(1 for p in self.pages_data if p.get("method") == "OCR")
        if ocr_count > 0:
            print(f"📸 Pages processed with OCR: {ocr_count}")
            print(f"📄 Pages with normal text: {normal_count}")
        
        self.pdfs_loaded = True
        return True
    
    def simple_search(self, question):
        """Simple keyword search as fallback"""
        question_lower = question.lower()
        results = []
        
        for i, line in enumerate(self.lines):
            if question_lower in line.lower():
                # Get context (line before, current line, 4 lines after)
                start = max(0, i - 1)
                end = min(len(self.lines), i + 5)
                
                context = []
                for j in range(start, end):
                    if self.lines[j].strip():
                        context.append(self.lines[j])
                
                results.append("\n".join(context))
                
                # Limit to first 3 results
                if len(results) >= 3:
                    break
        
        return results
    
    def find_relevant_sections(self, question, max_sections=3):
        """Find most relevant sections using keyword matching"""
        question_words = set(question.lower().split())
        scored_sections = []
        
        for page in self.pages_data:
            page_lower = page["text"].lower()
            score = 0
            
            # Score based on word matches
            for word in question_words:
                if len(word) > 2 and word in page_lower:
                    score += 1
            
            if score > 0:
                # Truncate long pages
                text_preview = page["text"][:1500] + "..." if len(page["text"]) > 1500 else page["text"]
                
                scored_sections.append({
                    "score": score,
                    "file": page["file"],
                    "page": page["page"],
                    "text": text_preview,
                    "method": page.get("method", "Unknown")
                })
        
        # Sort by score
        scored_sections.sort(key=lambda x: x["score"], reverse=True)
        
        return scored_sections[:max_sections]
    
    def ask_gemini(self, question):
        """Ask Gemini AI - handles both PDF questions and general chat"""
        try:
            # Check if it's a greeting or general conversation
            greetings = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
            is_greeting = any(greet in question.lower() for greet in greetings)
            
            if is_greeting:
                # Handle greetings directly without PDF context
                prompt = f"""You are a friendly PDF chatbot assistant. 
                The user said: "{question}"
                
                Respond in a friendly, welcoming way. Keep it brief and warm.
                If they have PDFs loaded, mention that they can ask questions about them.
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                return response.text, []
            
            # For other questions, check if we have PDFs
            if not self.pdfs_loaded or not self.pages_data:
                # No PDFs, just chat normally
                prompt = f"""You are a friendly AI assistant. The user asked: "{question}"
                
                Respond helpfully and conversationally. Since no PDFs are loaded, 
                just answer as a normal AI assistant would.
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                return response.text, []
            
            # We have PDFs - find relevant sections
            relevant_sections = self.find_relevant_sections(question)
            
            if relevant_sections:
                # Build context from relevant sections
                context = "Here are the most relevant sections from your PDFs:\n\n"
                for section in relevant_sections:
                    context += f"📄 [{section['file']} - Page {section['page']}] "
                    context += f"(Extracted via: {section['method']})\n"
                    context += f"{section['text']}\n\n"
                
                # Create prompt with PDF context
                prompt = f"""You are a helpful PDF document assistant. You have access to the following document sections:

{context}

USER QUESTION: {question}

INSTRUCTIONS:
1. FIRST, check if the question is about the PDFs or just general conversation
2. If it's a general question (like asking how you are, telling a joke, etc.), respond normally as a friendly AI
3. If it's about the PDFs, answer ONLY using information from the document sections above
4. If the answer isn't in the documents, say "I couldn't find information about that in the PDFs."
5. Be concise but include specific details
6. When possible, mention which document and page the information comes from
7. If the text was extracted via OCR, note that there might be minor OCR errors

ANSWER:"""
            else:
                # No relevant sections found, but still answer naturally
                prompt = f"""You are a friendly PDF chatbot assistant. The user asked: "{question}"

I've searched through their PDFs but couldn't find any relevant sections about this topic.

Please respond in one of these ways:
1. If it's a general question or greeting, answer normally
2. If it's asking about PDF content, politely say you couldn't find it in their documents
3. If you're not sure, offer to help with something else

Keep the response friendly and helpful.
"""
            
            # Get response from Gemini
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            
            return response.text, relevant_sections if relevant_sections else []
            
        except Exception as e:
            return f"😕 Sorry, I encountered an error: {str(e)}", []
    
    def chat(self):
        """Main chat loop"""
        if self.pdfs_loaded and self.pdf_files:
            print(f"\n✅ Loaded {len(self.pdf_files)} PDF file(s) successfully!")
        else:
            print("\n⚠️  No PDFs loaded - I'll just chat with you normally!")
        
        print("\n" + "="*70)
        print("🤖 Chatbot is ready! Let's chat! (Type 'help' for commands)")
        print("="*70)
        
        print("\n💡 Try saying 'hi' or asking me anything!")
        print("-"*70)
        
        use_simple_search = False
        
        while True:
            print()
            question = input("👤 You: ").strip()
            
            if question.lower() == "exit":
                print("🤖 Bye! Have a great day! 👋")
                break
            
            elif question.lower() == "help":
                print("\n📋 Available Commands:")
                print("   • 'exit' - Quit the program")
                print("   • 'help' - Show this help message")
                print("   • 'search' - Toggle between AI and simple search mode")
                print("   • 'list' - List all PDF files")
                print("   • 'stats' - Show processing statistics")
                print("   • 'mode' - Show current mode")
                print("\n💬 You can also:")
                print("   • Say 'hi', 'hello' for friendly chat")
                print("   • Ask questions about your PDFs")
                print("   • Ask general questions (I'll answer as a normal AI)")
                continue
            
            elif question.lower() == "list":
                if self.pdf_files:
                    print("\n📚 PDF Files:")
                    for i, pdf in enumerate(self.pdf_files, 1):
                        print(f"   {i}. {pdf}")
                else:
                    print("\n📚 No PDF files loaded.")
                continue
            
            elif question.lower() == "stats":
                print("\n📊 Statistics:")
                print(f"   PDF files: {len(self.pdf_files)}")
                print(f"   Pages processed: {len(self.pages_data)}")
                normal = sum(1 for p in self.pages_data if p.get("method") == "Normal")
                ocr = sum(1 for p in self.pages_data if p.get("method") == "OCR")
                print(f"   Normal text pages: {normal}")
                print(f"   OCR pages: {ocr}")
                print(f"   Total text: {len(self.documents)} characters")
                continue
            
            elif question.lower() == "mode":
                mode = "SIMPLE SEARCH" if use_simple_search else "GEMINI AI"
                print(f"\n🔄 Current mode: {mode}")
                continue
            
            elif question.lower() == "search":
                use_simple_search = not use_simple_search
                mode = "SIMPLE SEARCH 🔍" if use_simple_search else "GEMINI AI 🤖"
                print(f"✅ Switched to {mode} mode")
                continue
            
            if not question:
                print("🤖 Please say something!")
                continue
            
            # Simple Search Mode (only works if PDFs are loaded and have content)
            if use_simple_search:
                if not self.pdfs_loaded or not self.lines:
                    print("🤖 Simple search mode requires PDFs to be loaded first!")
                    continue
                    
                print("\n🔍 Searching PDFs...")
                results = self.simple_search(question)
                
                if results:
                    print(f"\n📖 Found {len(results)} relevant section(s):\n")
                    for i, result in enumerate(results, 1):
                        print(f"--- Result {i} ---")
                        print(result)
                        print()
                else:
                    print("\n❌ No relevant information found in PDFs")
            
            # Gemini AI Mode (handles everything)
            else:
                print("\n🤔 Thinking...")
                answer, sources = self.ask_gemini(question)
                
                print(f"\n🤖 {answer}")
                
                # Show sources if available and if they exist
                if sources:
                    print("\n📚 Sources:")
                    for source in sources:
                        print(f"   • {source['file']} (Page {source['page']}) - {source['method']}")

# -------- MAIN PROGRAM --------
if __name__ == "__main__":
    # Create and run chatbot
    chatbot = FriendlyPDFChatbot("pdfs")
    
    # Load PDFs (will work even if none exist)
    chatbot.load_pdfs()
    
    # Start chatting
    chatbot.chat()