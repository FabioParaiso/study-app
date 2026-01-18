from pypdf import PdfReader
import sys

try:
    reader = PdfReader("CN Clean.pdf")
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    print("--- RAW TEXT START ---")
    print(text[:2000]) # Print first 2000 chars
    print("--- RAW TEXT END ---")

except Exception as e:
    print(e)
