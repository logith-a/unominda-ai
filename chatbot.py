import fitz
import os

# -------- LOAD PDFs --------
pdf_folder = "pdfs"
documents = ""

for file in os.listdir(pdf_folder):
    if file.endswith(".pdf"):
        path = os.path.join(pdf_folder, file)
        doc = fitz.open(path)

        for page in doc:
            documents += page.get_text() + "\n"

print("PDFs loaded successfully ✅")


# -------- SPLIT INTO LINES --------
lines = documents.split("\n")


# -------- CHAT LOOP --------
while True:
    question = input("\nAsk a question (type 'exit' to quit): ")

    if question.lower() == "exit":
        break

    found = False

    for i, line in enumerate(lines):
        if question.lower() in line.lower():

            print("\nAnswer:\n")

            # Show this line + next 5 lines (paragraph)
            for j in range(i, min(i + 6, len(lines))):
                if lines[j].strip() != "":
                    print(lines[j])

            found = True
            break

    if not found:
        print("\nNo relevant answer found ❌")