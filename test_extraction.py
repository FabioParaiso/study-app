import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from pypdf import PdfReader
from logic import extract_topics

try:
    reader = PdfReader("CN Clean.pdf")
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    topics = extract_topics(text)
    print("--- EXTRACTED TOPICS ---")
    for t in topics:
        print(f"- {t}")
    print("--- END ---")

except Exception as e:
    print(e)
