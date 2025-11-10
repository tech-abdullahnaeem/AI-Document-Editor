"""
Check if Gemini API keys are working
Tests each key individually to verify functionality
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

def check_api_keys():
    """Check all API keys and report their status"""
    
    # Load .env file
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
    
    print("="*80)
    print("  GEMINI API KEY VERIFICATION")
    print("="*80)
    
    # Collect all API keys
    api_keys = []
    
    # Primary key
    primary_key = os.getenv('GEMINI_API_KEY')
    if primary_key:
        api_keys.append(('GEMINI_API_KEY', primary_key))
    
    # Backup keys
    for i in range(1, 31):
        key = os.getenv(f'API_KEY{i}')
        if key and key.strip():
            api_keys.append((f'API_KEY{i}', key))
    
    if not api_keys:
        print("\n❌ NO API KEYS FOUND!")
        print("Please set GEMINI_API_KEY in .env file")
        return
    
    print(f"\n✅ Found {len(api_keys)} API keys in .env file\n")
    
    # Test each key
    working_keys = []
    rate_limited_keys = []
    invalid_keys = []
    
    for key_name, key_value in api_keys:
        print(f"Testing {key_name}... ", end='', flush=True)
        
        try:
            # Configure with this key
            genai.configure(api_key=key_value)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            # Simple test prompt
            response = model.generate_content("Say 'OK' if you can read this.")
            
            if response and response.text:
                print(f"✅ WORKING - Response: {response.text.strip()[:20]}")
                working_keys.append(key_name)
            else:
                print(f"⚠️  WORKING but empty response")
                working_keys.append(key_name)
                
        except Exception as e:
            error_msg = str(e)
            
            if 'quota' in error_msg.lower() or 'rate limit' in error_msg.lower() or '429' in error_msg:
                print(f"⚠️  RATE LIMITED")
                rate_limited_keys.append(key_name)
            elif 'invalid' in error_msg.lower() or 'api key' in error_msg.lower() or '403' in error_msg or '401' in error_msg:
                print(f"❌ INVALID KEY")
                invalid_keys.append(key_name)
            else:
                print(f"❌ ERROR: {error_msg[:50]}")
                invalid_keys.append(key_name)
    
    # Summary
    print("\n" + "="*80)
    print("  SUMMARY")
    print("="*80)
    
    print(f"\n✅ Working keys: {len(working_keys)}")
    if working_keys:
        for key in working_keys[:5]:  # Show first 5
            print(f"   - {key}")
        if len(working_keys) > 5:
            print(f"   ... and {len(working_keys) - 5} more")
    
    print(f"\n⚠️  Rate limited keys: {len(rate_limited_keys)}")
    if rate_limited_keys:
        for key in rate_limited_keys[:5]:
            print(f"   - {key}")
        if len(rate_limited_keys) > 5:
            print(f"   ... and {len(rate_limited_keys) - 5} more")
    
    print(f"\n❌ Invalid/Error keys: {len(invalid_keys)}")
    if invalid_keys:
        for key in invalid_keys[:5]:
            print(f"   - {key}")
        if len(invalid_keys) > 5:
            print(f"   ... and {len(invalid_keys) - 5} more")
    
    print(f"\n📊 TOTAL: {len(api_keys)} keys ({len(working_keys)} working, {len(rate_limited_keys)} rate limited, {len(invalid_keys)} invalid)")
    
    if len(working_keys) == 0 and len(rate_limited_keys) == 0:
        print("\n❌ CRITICAL: No working API keys found!")
        print("   Please check your API keys at: https://makersuite.google.com/app/apikey")
    elif len(working_keys) == 0 and len(rate_limited_keys) > 0:
        print("\n⚠️  WARNING: All keys are rate limited!")
        print("   Wait a few minutes or add more API keys to .env file")
    else:
        print(f"\n✅ SUCCESS: {len(working_keys)} keys available for use")
        print(f"   API key rotation will distribute load across working keys")

if __name__ == "__main__":
    check_api_keys()
