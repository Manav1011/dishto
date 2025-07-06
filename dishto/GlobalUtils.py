import time
import uuid
import random
import string
import re
from google import genai
from qdrant_client import QdrantClient
import os

genai_client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY"),    
)

qdrant_client_ = QdrantClient(host=os.getenv("QDRANT_HOST","localhost"), port=int(os.getenv("QDRANT_PORT", 6333)))
print(f"Qdrant Client initialized with host: {os.getenv('QDRANT_HOST', 'localhost')} and port: {os.getenv('QDRANT_PORT', 6333)}")

def is_valid_email(email):
    # RFC 5322 compliant regex
    email_regex = re.compile(
        r"^(?!\.)"                            
        r"[-!#$%&'*+/=?^_`{|}~\w]+"           
        r"(?:\.[-!#$%&'*+/=?^_`{|}~\w]+)*"    
        r"(?<!\.)"                            
        r"@"                                  
        r"(?:(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}"
        r"|\[(?:\d{1,3}\.){3}\d{1,3}\])$"     
    )
    
    return re.match(email_regex, email) is not None

def generate_unique_hash():
    """
    Generates a more robust unique slug using a larger portion of UUID and timestamp.
    """
    # Use a larger part of UUID (32 characters) and append a timestamp for uniqueness
    random_hash = str(uuid.uuid4().hex)[:16]  # Using 16 characters from the UUID
    timestamp = str(int(time.time() * 1000))  # Millisecond precision timestamp
    
    # Combine UUID and timestamp for a more robust unique hash
    unique_hash = f"{random_hash}_{timestamp}"
    
    return unique_hash

def generate_temp_password(length=6):
    # Define the characters that can be used in the password (letters and digits)
    characters = string.ascii_letters + string.digits
    
    # Generate a random password by choosing random characters
    password = ''.join(random.choice(characters) for _ in range(length))
    
    return password

def normalize_email(email):
        """
        Normalize the email address by lowercasing the domain part of it.
        """
        email = email or ""
        try:
            email_name, domain_part = email.strip().rsplit("@", 1)
        except ValueError:
            pass
        else:            
            email = email_name.lower() + "@" + domain_part.lower()
        return email