"""
Test script for ISO 20022 Migration Service.

This script tests the converter with the sample MT103 from PROJECT_SPEC.md
"""

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

if __name__ == "__main__":
    from app.services.converter import convert_mt103_to_iso
    
    print("=" * 80)
    print("Testing MT103 to ISO 20022 pacs.008 Conversion")
    print("=" * 80)
    print("\nInput MT103:")
    print(sample_mt103)
    print("\n" + "=" * 80)
    
    try:
        xml_output = convert_mt103_to_iso(sample_mt103)
        print("\nConversion Successful!")
        print("=" * 80)
        print("\nOutput pacs.008 XML:")
        print(xml_output)
        print("\n" + "=" * 80)
        print("\n✅ Test PASSED")
    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
