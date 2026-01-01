#!/usr/bin/env python3
"""Direct test of MT102 converter to identify the error"""

from app.services.mt102_converter import MT102Parser, Pacs008Mapper

sample_mt102 = """:20:MULTI20231205001
:23:CRED
:32A:231205USD95000,00
:50K:/GB82WEST12345698765432
CORPORATE PAYMENTS LTD
250 BUSINESS PARK DRIVE
MANCHESTER M2 3BB
UNITED KINGDOM
:52A:NWBKGB2LXXX
:21:001
:32B:USD45000,00
:57A:CHASUS33XXX
:59:/US64SVBKUS6S3300958879
TECH SOLUTIONS INC
1500 MARKET STREET
SAN FRANCISCO CA 94103
USA
:70:INVOICE 2023-INV-1234
SOFTWARE LICENSE PAYMENT
:21:002
:32B:USD50000,00
:57A:BOFAUS3NXXX
:59:/US98BOFA00012345678900
CONSULTING PARTNERS LLC
789 FIFTH AVENUE
NEW YORK NY 10022
USA
:70:PROFESSIONAL SERVICES
DECEMBER 2023
:71A:SHA
"""

try:
    print("=" * 60)
    print("Testing MT102 Parser...")
    print("=" * 60)
    
    # Parse the message
    parsed = MT102Parser.parse(sample_mt102)
    
    print("\n✓ Parsing successful!")
    print(f"  Transaction Ref: {parsed.get('transaction_ref')}")
    print(f"  Currency: {parsed.get('currency')}")
    print(f"  Total Amount: {parsed.get('total_amount')}")
    print(f"  Number of transactions: {len(parsed.get('transactions', []))}")
    
    for i, txn in enumerate(parsed.get('transactions', []), 1):
        print(f"\n  Transaction {i}:")
        print(f"    Ref: {txn.get('transaction_ref')}")
        print(f"    Amount: {txn.get('currency')} {txn.get('amount')}")
        print(f"    Beneficiary Bank: {txn.get('beneficiary_bank', 'N/A')[:30]}...")
    
    print("\n" + "=" * 60)
    print("Testing Pacs008Mapper...")
    print("=" * 60)
    
    # Convert to pacs.008
    pacs008_doc = Pacs008Mapper.map_to_pacs008(parsed)
    
    print("\n✓ Mapping successful!")
    print(f"  Message ID: {pacs008_doc.FIToFICstmrCdtTrf.GrpHdr.MsgId}")
    print(f"  Number of transactions: {pacs008_doc.FIToFICstmrCdtTrf.GrpHdr.NbOfTxs}")
    print(f"  Transactions: {len(pacs008_doc.FIToFICstmrCdtTrf.CdtTrfTxInf)}")
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
