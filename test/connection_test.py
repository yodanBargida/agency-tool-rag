import os
from dotenv import load_dotenv
from langfuse import Langfuse

# Load .env
load_dotenv()

def test_langfuse_connection():
    print("--- Langfuse Connection Test ---")
    
    # 2026 SDKs prefer BASE_URL
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    base_url = os.getenv("LANGFUSE_BASE_URL") or os.getenv("LANGFUSE_HOST")
    
    print(f"URL: {base_url}")
    print(f"Public Key: {public_key[:7]}...")
    
    # Initialize client
    langfuse = Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        base_url=base_url
    )
    
    # The auth_check() method is the gold standard for debugging 401s
    if langfuse.auth_check():
        print("✅ SUCCESS: Authenticated successfully!")
        
        # Try sending a dummy trace to be 100% sure
        trace = langfuse.trace(name="connection_test_trace")
        trace.span(name="test_span", input="hello", output="world")
        langfuse.flush()
        print("✅ SUCCESS: Dummy trace sent and flushed.")
    else:
        print("❌ ERROR: Authentication failed (401).")
        print("Check if:")
        print("1. Your Public Key starts with 'pk-lf-' and Secret with 'sk-lf-'")
        print("2. Your BASE_URL matches your project region (US vs EU)")

if __name__ == "__main__":
    test_langfuse_connection()