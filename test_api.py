"""
API test script using httpx to test the /convert endpoint.
"""

import httpx
import json

# Sample MT103 from PROJECT_SPEC.md
sample_mt103 = """
:20:TRF123456789
:32A:231005USD10000,
:50K:/1234567890
JOHN DOE
123 MAIN ST
NEW YORK, NY
:59:/0987654321
JANE SMITH
456 HIGH ST
LONDON, UK
:71A:OUR
"""

def test_health_check():
    """Test the health check endpoint"""
    print("\n" + "=" * 80)
    print("Testing Health Check Endpoint")
    print("=" * 80)
    
    try:
        response = httpx.get("http://localhost:8000/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_convert_endpoint():
    """Test the /convert endpoint"""
    print("\n" + "=" * 80)
    print("Testing /convert Endpoint")
    print("=" * 80)
    
    payload = {
        "mt103_message": sample_mt103
    }
    
    try:
        response = httpx.post(
            "http://localhost:8000/convert",
            json=payload,
            timeout=10.0
        )
        print(f"Status Code: {response.status_code}")
        
        result = response.json()
        
        if result.get("success"):
            print("\n✅ Conversion Successful!")
            print(f"Input Hash: {result['input_hash']}")
            print(f"Timestamp: {result['timestamp']}")
            print("\nGenerated XML (first 500 chars):")
            print(result['pacs008_xml'][:500] + "...")
        else:
            print("\n❌ Conversion Failed!")
            print(f"Errors: {result.get('errors')}")
        
        return result.get("success", False)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_stats_endpoint():
    """Test the /stats endpoint"""
    print("\n" + "=" * 80)
    print("Testing /stats Endpoint")
    print("=" * 80)
    
    try:
        response = httpx.get("http://localhost:8000/stats")
        print(f"Status Code: {response.status_code}")
        print(f"Stats: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "🚀 " * 40)
    print("ISO 20022 Migration Service - API Tests")
    print("🚀 " * 40)
    
    # Test endpoints
    health_ok = test_health_check()
    convert_ok = test_convert_endpoint()
    stats_ok = test_stats_endpoint()
    
    # Summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Convert Endpoint: {'✅ PASS' if convert_ok else '❌ FAIL'}")
    print(f"Stats Endpoint: {'✅ PASS' if stats_ok else '❌ FAIL'}")
    
    if all([health_ok, convert_ok, stats_ok]):
        print("\n🎉 All tests PASSED!")
    else:
        print("\n⚠️ Some tests FAILED")
