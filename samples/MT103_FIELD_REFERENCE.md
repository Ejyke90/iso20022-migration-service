# MT103 Field Specifications and Mappings

## Mandatory Fields

| Field | Tag | Description | Format | Mandatory |
|-------|-----|-------------|--------|-----------|
| Transaction Reference | :20: | Unique reference assigned by sender | 16x | ✓ YES |
| Bank Operation Code | :23B: | Type of payment (CRED, SPAY, SPRI, SSTD) | 4!c | ✓ YES |
| Value Date/Currency/Amount | :32A: | Settlement date, currency, amount | 6!n3!a15d | ✓ YES |
| Ordering Customer | :50K: | Payer details | 35x (4 lines) | ✓ YES |
| Beneficiary Customer | :59: | Payee details | 35x (4 lines) | ✓ YES |
| Details of Charges | :71A: | Who bears charges (OUR/BEN/SHA) | 3!a | ✓ YES |

## Optional But Common Fields

| Field | Tag | Description | ISO 20022 Mapping |
|-------|-----|-------------|-------------------|
| Instruction Code | :23E: | Additional instructions | `PmtTpInf/InstrPrty` |
| Transaction Type Code | :26T: | Type of transaction | `PmtTpInf/CtgyPurp` |
| Currency/Amount | :33B: | Original amount if different | `InstdAmt` |
| Exchange Rate | :36: | FX rate if applicable | `XchgRate` |
| Ordering Institution | :52A/D: | Sender's bank | `InstgAgt` |
| Sender's Correspondent | :53A/B/D: | Intermediary bank | `IntrmyAgt1` |
| Receiver's Correspondent | :54A/B/D: | Receiving intermediary | `IntrmyAgt2` |
| Intermediary | :56A/C/D: | Another intermediary | `IntrmyAgt` |
| Account With Institution | :57A/B/C/D: | Beneficiary's bank | `CdtrAgt` |
| Beneficiary | :59:/59A: | Final beneficiary | `Cdtr` |
| Remittance Information | :70: | Payment details | `RmtInf/Ustrd` |
| Sender's Charges | :71F: | Charges borne by sender | `ChrgsInf` |
| Receiver's Charges | :71G: | Charges borne by receiver | `ChrgsInf` |
| Sender to Receiver Info | :72: | Bank-to-bank info | `InstrForCdtrAgt` |

## Bank Operation Codes (:23B:)

- **CRED**: Credit Transfer (most common)
- **SPAY**: Payment against a previous delivery
- **SPRI**: Payment with priority
- **SSTD**: Standard payment

## Charge Bearer Codes (:71A:)

- **OUR**: All charges for ordering customer → Maps to `DEBT`
- **BEN**: All charges for beneficiary → Maps to `CRED`
- **SHA**: Charges shared → Maps to `SHAR`

## ISO 20022 pacs.008 Structure

```
Document
└── FIToFICstmrCdtTrf (FI To FI Customer Credit Transfer)
    ├── GrpHdr (Group Header)
    │   ├── MsgId (Message ID from :20:)
    │   ├── CreDtTm (Creation DateTime)
    │   ├── NbOfTxs (Number of Transactions = "1")
    │   └── SttlmInf (Settlement Information)
    │       └── SttlmMtd (Settlement Method)
    └── CdtTrfTxInf (Credit Transfer Transaction Info)
        ├── PmtId (Payment Identification)
        │   ├── InstrId (from :20:)
        │   ├── EndToEndId (from :20:)
        │   └── TxId (generated)
        ├── PmtTpInf (Payment Type Info from :23B:, :23E:, :26T:)
        ├── IntrBkSttlmAmt (from :32A: amount)
        ├── IntrBkSttlmDt (from :32A: date)
        ├── InstdAmt (from :33B: if present)
        ├── XchgRate (from :36: if present)
        ├── ChrgBr (from :71A:)
        ├── ChrgsInf (from :71F:, :71G:)
        ├── InstgAgt (from :52:)
        ├── InstdAgt (from :57:)
        ├── IntrmyAgt1 (from :56:)
        ├── Dbtr (from :50K:)
        ├── DbtrAcct (account from :50K:)
        ├── DbtrAgt (from :52:)
        ├── CdtrAgt (from :57:)
        ├── Cdtr (from :59:)
        ├── CdtrAcct (account from :59:)
        ├── RmtInf (from :70:)
        └── InstrForCdtrAgt (from :72:)
```

## Sample Conversions

### Basic Transfer
```
MT103 :20:TRF123456789
      :23B:CRED
      :32A:231005USD10000,
      :50K:/1234567890
           JOHN DOE
      :59:/0987654321
           JANE SMITH
      :71A:OUR

ISO 20022: Creates pacs.008 with:
- MsgId from :20:
- IntrBkSttlmAmt: USD 10000
- Dbtr: JOHN DOE
- Cdtr: JANE SMITH
- ChrgBr: DEBT (from OUR)
```

### International Transfer with All Fields
```
MT103 :20:WIRE123
      :23B:CRED
      :23E:SDVA
      :32A:231220EUR50000,
      :33B:EUR50000,
      :50K:/DE89370400440532013000
           MUELLER GMBH
      :52A:DEUTDEFFXXX
      :56A:CHASUS33XXX
      :57A:NWBKGB2LXXX
      :59:/GB29NWBK60161331926819
           SMITH LTD
      :70:INVOICE 12345
      :71A:SHA
      :71F:EUR15,00
      :72:/INS/URGENT

ISO 20022: Creates pacs.008 with:
- Full agent chain (InstgAgt, IntrmyAgt, InstdAgt, CdtrAgt)
- Charges information
- Bank-to-bank instructions
- Remittance details
```
