#!/usr/bin/env python3
"""
Test all Gemini API keys with a simple hello request
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai
import time

# Load environment variables
env_path = '/Users/abdullah/Desktop/Techinoid/final with fast api copy/.env'
load_dotenv(env_path)

print("=" * 70)
print("TESTING GEMINI API KEYS")
print("=" * 70)

# Collect all API keys
api_keys = {}

# Primary key
primary = os.getenv('GEMINI_API_KEY')
if primary:
    api_keys['GEMINI_API_KEY'] = primary

# Numbered keys (API_KEY1 to API_KEY39)
for i in range(1, 40):
    key = os.getenv(f'API_KEY{i}')
    if key:
        api_keys[f'API_KEY{i}'] = key

print(f"\n📊 Found {len(api_keys)} API keys in .env file")
print(f"🧪 Testing each key with a simple 'hello' request...\n")

working_keys = []
rate_limited_keys = []
invalid_keys = []
error_keys = []

for key_name, key_value in api_keys.items():
    key_display = f"{key_name}: {key_value[:15]}...{key_value[-5:]}"
    print(f"{key_display:50} ", end="", flush=True)
    
    try:
        genai.configure(api_key=key_value)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Simple hello request with minimal tokens
        response = model.generate_content("Say hello")
        
        result_text = response.text.strip()
        print(f"✅ OK ({result_text[:20]})")
        working_keys.append(key_name)
        time.sleep(0.5)  # Small delay to avoid triggering rate limits
        
    except Exception as e:
        error_msg = str(e)
        
        # Check for specific error types
        if "429" in error_msg or "Resource has been exhausted" in error_msg:
            print(f"⏳ RATE LIMITED")
            rate_limited_keys.append(key_name)
        elif "quota" in error_msg.lower():
            print(f"📊 QUOTA EXCEEDED")
            rate_limited_keys.append(key_name)
        elif "403" in error_msg or "API_KEY_INVALID" in error_msg:
            print(f"❌ INVALID KEY")
            invalid_keys.append(key_name)
        elif "400" in error_msg:
            print(f"⚠️  BAD REQUEST")
            error_keys.append(key_name)
        else:
            print(f"❌ ERROR: {error_msg[:30]}")
            error_keys.append(key_name)
        
        time.sleep(0.5)

# Summary
print("\n" + "=" * 70)
print("TEST RESULTS SUMMARY")
print("=" * 70)

total = len(api_keys)
print(f"\n📊 Total Keys Tested: {total}")

print(f"\n✅ Working Keys: {len(working_keys)}/{total} ({len(working_keys)/total*100:.1f}%)")
if working_keys:
    for i, key in enumerate(working_keys, 1):
        print(f"   {i}. {key}")

print(f"\n⏳ Rate Limited Keys: {len(rate_limited_keys)}/{total} ({len(rate_limited_keys)/total*100:.1f}%)")
if rate_limited_keys:
    for i, key in enumerate(rate_limited_keys[:10], 1):
        print(f"   {i}. {key}")
    if len(rate_limited_keys) > 10:
        print(f"   ... and {len(rate_limited_keys) - 10} more")

print(f"\n❌ Invalid Keys: {len(invalid_keys)}/{total}")
if invalid_keys:
    for i, key in enumerate(invalid_keys, 1):
        print(f"   {i}. {key}")

print(f"\n⚠️  Error Keys: {len(error_keys)}/{total}")
if error_keys:
    for i, key in enumerate(error_keys, 1):
        print(f"   {i}. {key}")

# Recommendations
print("\n" + "=" * 70)
print("RECOMMENDATIONS")
print("=" * 70)

if len(working_keys) >= 5:
    print(f"✅ {len(working_keys)} keys are working - Good for testing!")
    print(f"   Estimated capacity: {len(working_keys) * 15} requests/minute")
    print(f"   Estimated capacity: {len(working_keys) * 1500} requests/day")
elif len(working_keys) > 0:
    print(f"⚠️  Only {len(working_keys)} key(s) working - Limited capacity")
    print(f"   Estimated capacity: {len(working_keys) * 15} requests/minute")
    print(f"   Reduce test frequency or wait for quota reset")
else:
    print(f"❌ NO WORKING KEYS FOUND!")
    print(f"\nPossible reasons:")
    print(f"   1. All keys hit daily quota (1,500 requests/day)")
    print(f"   2. Rate limit exceeded (15 requests/minute)")
    print(f"   3. Keys are invalid or expired")
    print(f"\nSolutions:")
    print(f"   1. Wait for quota reset (midnight Pacific Time)")
    print(f"   2. Check .env file for correct API keys")
    print(f"   3. Get new API keys from https://makersuite.google.com/app/apikey")

if len(rate_limited_keys) > 0:
    print(f"\n📋 Rate Limit Info:")
    print(f"   • Free tier: 15 requests/minute, 1,500 requests/day")
    print(f"   • Quotas reset daily at midnight Pacific Time")
    print(f"   • Current time: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}")

print("\n" + "=" * 70 + "\n")

# Save results to file
with open('api_key_test_results.txt', 'w') as f:
    f.write(f"API Key Test Results - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 70 + "\n\n")
    f.write(f"Total Keys: {total}\n")
    f.write(f"Working: {len(working_keys)}\n")
    f.write(f"Rate Limited: {len(rate_limited_keys)}\n")
    f.write(f"Invalid: {len(invalid_keys)}\n")
    f.write(f"Errors: {len(error_keys)}\n\n")
    
    if working_keys:
        f.write("Working Keys:\n")
        for key in working_keys:
            f.write(f"  - {key}\n")

print(f"📄 Results saved to: api_key_test_results.txt")
