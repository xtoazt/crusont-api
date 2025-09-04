#!/usr/bin/env python3
"""
Simple test script to verify API endpoints work
"""
import requests
import json

def test_endpoint(url, endpoint, expected_status=200):
    """Test a single endpoint"""
    full_url = f"{url}{endpoint}"
    try:
        response = requests.get(full_url, timeout=10)
        print(f"✅ {endpoint} - Status: {response.status_code}")
        if response.status_code == expected_status:
            try:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
            except:
                print(f"   Response: {response.text[:200]}...")
        else:
            print(f"   ❌ Expected {expected_status}, got {response.status_code}")
        return response.status_code == expected_status
    except Exception as e:
        print(f"❌ {endpoint} - Error: {e}")
        return False

def main():
    # Test against deployed URL (replace with your actual URL)
    base_url = "https://your-deployment.vercel.app"
    
    print("🧪 Testing Crusont API Endpoints")
    print("=" * 50)
    
    endpoints = [
        ("/", 200),
        ("/health", 200),
        ("/test", 200),
        ("/v1/models", 200),
        ("/favicon.ico", 200),
        ("/robots.txt", 200),
        ("/sitemap.xml", 200),
        ("/manifest.json", 200),
        ("/styles.css", 200),
        ("/script.js", 200),
    ]
    
    success_count = 0
    total_count = len(endpoints)
    
    for endpoint, expected_status in endpoints:
        if test_endpoint(base_url, endpoint, expected_status):
            success_count += 1
        print()
    
    print("=" * 50)
    print(f"Results: {success_count}/{total_count} endpoints working")
    
    if success_count == total_count:
        print("🎉 All endpoints working correctly!")
    else:
        print("⚠️  Some endpoints have issues")

if __name__ == "__main__":
    main()
