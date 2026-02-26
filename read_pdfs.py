import fitz
import os

pdf_folder = "pdfs"
all_text = ""

for file in os.listdir(pdf_folder):
    if file.endswith(".pdf"):
        path = os.path.join(pdf_folder, file)
        print("Reading:", file)

        doc = fitz.open(path)

        for page in doc:
            all_text += page.get_text()

print("\n===== EXTRACTED TEXT =====\n")
print(all_text[:1000])