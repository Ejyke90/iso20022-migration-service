#!/usr/bin/env python3
"""
Interactive Test Script - Easy way to test MT103 conversions

Usage:
    python interactive_test.py
"""

import requests
import json
from pathlib import Path

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_conversion(mt103_file):
    """Test a single MT103 file conversion"""
    print(f"\n📄 Testing: {mt103_file.name}")
    print("-" * 80)
    
    # Read MT103 file
    with open(mt103_file, 'r') as f:
        mt103_content = f.read()
    
    print("Input MT103:")
    print(mt103_content)
    print("-" * 80)
    
    # Send request
    try:
        response = requests.post(
            'http://localhost:8000/convert',
            json={'mt103_message': mt103_content},
            timeout=5.0
        )
        
        result = response.json()
        
        if result['success']:
            print("✅ Conversion Successful!")
            print(f"\nInput Hash: {result['input_hash'][:16]}...")
            print(f"Timestamp: {result['timestamp']}")
            
            # Save XML to file
            output_file = f"output_{mt103_file.stem}.xml"
            with open(output_file, 'w') as f:
                f.write(result['pacs008_xml'])
            
            print(f"\n💾 XML saved to: {output_file}")
            
            # Show preview
            xml_lines = result['pacs008_xml'].split('\n')
            print("\nXML Preview (first 20 lines):")
            print("-" * 80)
            for line in xml_lines[:20]:
                print(line)
            if len(xml_lines) > 20:
                print(f"... ({len(xml_lines) - 20} more lines)")
            
            return True
        else:
            print("❌ Conversion Failed!")
            print(f"\nErrors:")
            for error in result.get('errors', []):
                print(f"  - {error}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to server!")
        print("\nMake sure the server is running:")
        print("  python -m uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print_header("ISO 20022 Migration Service - Interactive Test")
    
    # Check if server is running
    try:
        response = requests.get('http://localhost:8000/', timeout=2.0)
        health = response.json()
        print(f"\n✅ Server is running - Status: {health['status']}")
        print(f"   Version: {health['version']}")
    except:
        print("\n❌ Server is not running!")
        print("\nPlease start the server first:")
        print("  python -m uvicorn app.main:app --reload")
        print("\nOr:")
        print("  python app/main.py")
        return
    
    # Find sample files
    samples_dir = Path('samples')
    if not samples_dir.exists():
        print("\n❌ samples/ directory not found!")
        return
    
    sample_files = sorted(samples_dir.glob('*.txt'))
    
    if not sample_files:
        print("\n❌ No sample files found in samples/")
        return
    
    print(f"\n📁 Found {len(sample_files)} sample file(s)")
    
    # Test each file
    print_header("Running Conversions")
    
    results = []
    for sample_file in sample_files:
        success = test_conversion(sample_file)
        results.append((sample_file.name, success))
        print()
    
    # Summary
    print_header("Test Summary")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    print("\nResults:")
    for filename, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {filename}")
    
    # Show statistics
    print_header("Server Statistics")
    try:
        response = requests.get('http://localhost:8000/stats')
        stats = response.json()
        print(f"\nTotal Conversions: {stats['total_conversions']}")
        print(f"Successful: {stats['successful']}")
        print(f"Failed: {stats['failed']}")
        print(f"Success Rate: {stats['success_rate']}%")
    except:
        print("\n⚠️ Could not retrieve statistics")
    
    # Show generated files
    print_header("Generated Files")
    output_files = list(Path('.').glob('output_*.xml'))
    if output_files:
        print("\nGenerated XML files:")
        for f in output_files:
            size_kb = f.stat().st_size / 1024
            print(f"  📄 {f.name} ({size_kb:.1f} KB)")
    else:
        print("\nNo output files generated")
    
    print("\n" + "=" * 80)
    print("🎉 Testing complete!")
    print("\nTo view API documentation: http://localhost:8000/docs")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
