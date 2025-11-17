#!/usr/bin/env python3
"""
Test script for CodeShield AI Backend
Tests all endpoints and functionality
"""

import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_health_check() -> bool:
    """Test the health check endpoint."""
    print("[TEST] Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] Health check passed: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"[FAIL] Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[FAIL] Cannot connect to server. Is it running?")
        return False
    except Exception as e:
        print(f"[FAIL] Health check error: {str(e)}")
        return False

def test_root_endpoint() -> bool:
    """Test the root endpoint."""
    print("\n[TEST] Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] Root endpoint works: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"[FAIL] Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Root endpoint error: {str(e)}")
        return False

def test_analyze_endpoint() -> bool:
    """Test the analyze endpoint with sample code."""
    print("\n[TEST] Testing analyze endpoint...")
    
    # Sample vulnerable code
    test_code = """
def login(username, password):
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    result = execute_query(query)
    return result
"""
    
    try:
        response = requests.post(
            f"{BASE_URL}/analyze",
            json={"code": test_code},
            headers={"Content-Type": "application/json"},
            timeout=30  # Gemini API might take time
        )
        
        if response.status_code == 200:
            data = response.json()
            print("[PASS] Analyze endpoint works!")
            print(f"   Risk Score: {data.get('risk_score', 'N/A')}")
            print(f"   Vulnerabilities found: {len(data.get('vulnerabilities', []))}")
            print(f"   Fixes suggested: {len(data.get('fixes', []))}")
            print(f"   Explanation: {data.get('explanation', '')[:100]}...")
            return True
        else:
            print(f"[FAIL] Analyze endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print("[WARN] Analyze endpoint timed out (this is normal for first Gemini API call)")
        return False
    except Exception as e:
        print(f"[FAIL] Analyze endpoint error: {str(e)}")
        return False

def test_analyze_endpoint_v1() -> bool:
    """Test the versioned analyze endpoint."""
    print("\n[TEST] Testing /api/v1/analyze endpoint...")
    
    test_code = "def test(): return 'hello'"
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/analyze",
            json={"code": test_code},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("[PASS] /api/v1/analyze endpoint works!")
            return True
        else:
            print(f"[FAIL] /api/v1/analyze failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] /api/v1/analyze error: {str(e)}")
        return False

def test_history_endpoint() -> bool:
    """Test the history endpoint."""
    print("\n[TEST] Testing history endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/analyze/history?limit=5", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] History endpoint works!")
            print(f"   Response structure: {json.dumps(data, indent=2)[:200]}...")
            return True
        else:
            print(f"[FAIL] History endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] History endpoint error: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("CodeShield AI Backend Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test basic endpoints
    results.append(("Health Check", test_health_check()))
    results.append(("Root Endpoint", test_root_endpoint()))
    
    # Test analyze endpoints
    results.append(("Analyze Endpoint", test_analyze_endpoint()))
    results.append(("Analyze Endpoint V1", test_analyze_endpoint_v1()))
    
    # Test history
    results.append(("History Endpoint", test_history_endpoint()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

