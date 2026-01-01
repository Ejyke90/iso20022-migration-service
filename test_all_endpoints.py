#!/usr/bin/env python3
"""Comprehensive test of all message type endpoints"""

import requests
import json
from time import sleep

API_URL = "http://127.0.0.1:8000"

# Test samples
samples = {
    "MT103": {
        "endpoint": "/convert",
        "payload": {
            "mt103_message": """:20:TRF123456789
:32A:231005USD10000,
:50K:/1234567890
JOHN DOE
123 MAIN ST
NEW YORK, NY
:59:/0987654321
JANE SMITH
456 HIGH ST
LONDON, UK
:71A:OUR"""
        }
    },
    "MT101": {
        "endpoint": "/convert/mt101",
        "payload": {
            "mt101_message": """:20:PAY20231201001
:23:CRED
:50K:/GB82WEST12345698765432
CORPORATE PAYMENTS LTD
:32A:231201EUR150000,00
:50K:/GB82WEST12345698765432
CORPORATE PAYMENTS LTD
:32B:EUR75000,00
:59:/DE89370400440532013000
SUPPLIER ONE GMBH
:70:INVOICE INV-2023-001
:32B:EUR75000,00
:59:/FR1420041010050500013M02606
VENDOR DEUX SARL
:70:PAYMENT FOR SERVICES"""
        }
    },
    "MT102": {
        "endpoint": "/convert/mt102",
        "payload": {
            "mt103_message": """:20:MULTI20231205001
:23:CRED
:32A:231205USD95000,00
:50K:/GB82WEST12345698765432
CORPORATE PAYMENTS LTD
:52A:NWBKGB2LXXX
:21:001
:32B:USD45000,00
:57A:CHASUS33XXX
:59:/US64SVBKUS6S3300958879
TECH SOLUTIONS INC
:70:INVOICE 2023-INV-1234
:21:002
:32B:USD50000,00
:57A:BOFAUS3NXXX
:59:/US98BOFA00012345678900
CONSULTING PARTNERS LLC
:70:PROFESSIONAL SERVICES
:71A:SHA"""
        }
    },
    "MT202": {
        "endpoint": "/convert/mt202",
        "payload": {
            "mt202_message": """:20:COV20231210001
:21:RELREF123456
:32A:231210USD250000,00
:52A:CHASUS33XXX
:53A:DEUTDEFFXXX
:58A:BNPAFRPPXXX
:72:/INS/SHA
/ACC/COVER FOR CUSTOMER PAYMENT"""
        }
    }
}

def test_endpoint(name, endpoint, payload):
    """Test a single endpoint"""
    print(f"\n{'='*70}")
    print(f"Testing {name}")
    print(f"{'='*70}")
    
    try:
        response = requests.post(
            f"{API_URL}{endpoint}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ SUCCESS")
                # Show first 500 chars of XML
                xml = data.get('pacs008_xml') or data.get('pain001_xml') or data.get('pacs009_xml')
                if xml:
                    print(f"XML Output (first 500 chars):\n{xml[:500]}...")
            else:
                print(f"❌ FAILED")
                print(f"Errors: {data.get('errors')}")
        elif response.status_code == 422:
            print(f"❌ VALIDATION ERROR (422)")
            try:
                error_detail = response.json()
                print(f"Detail: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Response: {response.text}")
        else:
            print(f"❌ ERROR {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR - Is the server running?")
    except Exception as e:
        print(f"❌ EXCEPTION: {type(e).__name__}: {e}")

def main():
    print(f"\n{'#'*70}")
    print(f"# ISO 20022 Migration Service - Endpoint Tests")
    print(f"# Testing all message types")
    print(f"{'#'*70}")
    
    # Test each endpoint
    for name, config in samples.items():
        test_endpoint(name, config['endpoint'], config['payload'])
        sleep(0.5)  # Small delay between tests
    
    print(f"\n{'#'*70}")
    print(f"# All tests completed")
    print(f"{'#'*70}\n")

if __name__ == "__main__":
    main()
