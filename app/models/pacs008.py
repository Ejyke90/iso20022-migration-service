"""
Pydantic models for MT103 input and ISO 20022 pacs.008.001.08 output.

This module defines the data structures for:
1. MT103 input validation
2. ISO 20022 pacs.008 XML message hierarchy
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, validator, field_validator
from enum import Enum


# ============================================================================
# MT103 Input Models
# ============================================================================

class MT103Message(BaseModel):
    """
    Pydantic model for validating raw MT103 SWIFT message input.
    
    MT103 is the SWIFT message type for Single Customer Credit Transfer.
    """
    raw_message: str = Field(
        ...,
        description="Raw MT103 message text block",
        min_length=10
    )
    
    # Parsed fields (extracted from raw_message)
    transaction_reference: Optional[str] = Field(
        None,
        description="Field :20: - Transaction Reference Number",
        alias="field_20"
    )
    value_date: Optional[str] = Field(
        None,
        description="Field :32A: - Value Date (YYMMDD)",
        alias="field_32a_date"
    )
    currency: Optional[str] = Field(
        None,
        description="Field :32A: - Currency Code (3 chars)",
        alias="field_32a_currency",
        min_length=3,
        max_length=3
    )
    amount: Optional[str] = Field(
        None,
        description="Field :32A: - Transaction Amount",
        alias="field_32a_amount"
    )
    ordering_customer: Optional[str] = Field(
        None,
        description="Field :50K: - Ordering Customer (multiline)",
        alias="field_50k"
    )
    beneficiary_customer: Optional[str] = Field(
        None,
        description="Field :59: - Beneficiary Customer (multiline)",
        alias="field_59"
    )
    details_of_charges: Optional[str] = Field(
        None,
        description="Field :71A: - Details of Charges (OUR/BEN/SHA)",
        alias="field_71a"
    )
    
    class Config:
        populate_by_name = True


# ============================================================================
# ISO 20022 pacs.008 Output Models (Nested Structure)
# ============================================================================

class ChargeBearer(str, Enum):
    """Charge Bearer Code - ISO 20022 ChargeBearerType1Code"""
    DEBT = "DEBT"  # Borne by debtor
    CRED = "CRED"  # Borne by creditor
    SHAR = "SHAR"  # Shared
    SLEV = "SLEV"  # Service level


class SettlementMethod(str, Enum):
    """Settlement Method Code - ISO 20022 SettlementMethod1Code"""
    INDA = "INDA"  # Instructed agent
    INGA = "INGA"  # Instructing agent
    COVE = "COVE"  # Cover method
    CLRG = "CLRG"  # Clearing system


# ============================================================================
# Common/Reusable Components
# ============================================================================

class PostalAddress(BaseModel):
    """Postal Address - PostalAddress24"""
    StrtNm: Optional[str] = Field(None, description="Street Name", max_length=70)
    BldgNb: Optional[str] = Field(None, description="Building Number", max_length=16)
    PstCd: Optional[str] = Field(None, description="Post Code", max_length=16)
    TwnNm: Optional[str] = Field(None, description="Town Name", max_length=35)
    CtrySubDvsn: Optional[str] = Field(None, description="Country Sub Division", max_length=35)
    Ctry: Optional[str] = Field(None, description="Country", min_length=2, max_length=2)
    AdrLine: Optional[List[str]] = Field(
        None,
        description="Address Line (max 7 lines, 70 chars each)",
        max_length=7
    )
    
    @field_validator('AdrLine')
    @classmethod
    def validate_address_lines(cls, v):
        if v:
            for line in v:
                if len(line) > 70:
                    raise ValueError("Address line cannot exceed 70 characters")
        return v


class AccountIdentification(BaseModel):
    """Account Identification - Other"""
    Id: str = Field(..., description="Account Identification", max_length=34)


class AccountIdentificationOther(BaseModel):
    """Account Identification - GenericAccountIdentification1"""
    Othr: AccountIdentification = Field(..., description="Other Account Identification")


class AccountSchemeName(BaseModel):
    """Account Scheme Name"""
    Cd: Optional[str] = Field(None, description="Code")
    Prtry: Optional[str] = Field(None, description="Proprietary")


class CashAccount(BaseModel):
    """Cash Account - CashAccount38"""
    Id: AccountIdentificationOther = Field(..., description="Account Identification")
    Ccy: Optional[str] = Field(None, description="Currency", min_length=3, max_length=3)


class FinancialInstitutionIdentification(BaseModel):
    """Financial Institution Identification - FinancialInstitutionIdentification18"""
    BICFI: Optional[str] = Field(None, description="BIC (Bank Identifier Code)", max_length=11)
    ClrSysMmbId: Optional[dict] = Field(None, description="Clearing System Member Identification")
    Nm: Optional[str] = Field(None, description="Name", max_length=140)
    PstlAdr: Optional[PostalAddress] = Field(None, description="Postal Address")


class BranchAndFinancialInstitutionIdentification(BaseModel):
    """Branch and Financial Institution Identification - BranchAndFinancialInstitutionIdentification6"""
    FinInstnId: FinancialInstitutionIdentification = Field(
        ...,
        description="Financial Institution Identification"
    )


class Party(BaseModel):
    """Party Identification - PartyIdentification135"""
    Nm: Optional[str] = Field(None, description="Name", max_length=140)
    PstlAdr: Optional[PostalAddress] = Field(None, description="Postal Address")
    Id: Optional[dict] = Field(None, description="Party Identification")
    CtryOfRes: Optional[str] = Field(None, description="Country of Residence", min_length=2, max_length=2)


class ActiveOrHistoricCurrencyAndAmount(BaseModel):
    """Active or Historic Currency and Amount - ActiveOrHistoricCurrencyAndAmount"""
    Ccy: str = Field(..., description="Currency Code", min_length=3, max_length=3)
    value: Decimal = Field(..., description="Amount Value", gt=0, alias="Value")
    
    class Config:
        populate_by_name = True
    
    @field_validator('value')
    @classmethod
    def validate_positive_amount(cls, v):
        if v <= 0:
            raise ValueError("Settlement amount must be positive")
        return v


class PaymentIdentification(BaseModel):
    """Payment Identification - PaymentIdentification13"""
    InstrId: Optional[str] = Field(None, description="Instruction Identification", max_length=35)
    EndToEndId: str = Field(..., description="End To End Identification", max_length=35)
    TxId: Optional[str] = Field(None, description="Transaction Identification", max_length=35)
    UETR: Optional[str] = Field(None, description="Unique End-to-end Transaction Reference")


class PaymentTypeInformation(BaseModel):
    """Payment Type Information - PaymentTypeInformation28"""
    InstrPrty: Optional[str] = Field(None, description="Instruction Priority")
    SvcLvl: Optional[dict] = Field(None, description="Service Level")
    LclInstrm: Optional[dict] = Field(None, description="Local Instrument")
    CtgyPurp: Optional[dict] = Field(None, description="Category Purpose")


class SettlementInstruction(BaseModel):
    """Settlement Information - SettlementInstruction7"""
    SttlmMtd: SettlementMethod = Field(
        ...,
        description="Settlement Method Code"
    )
    InstgRmbrsmntAgt: Optional[BranchAndFinancialInstitutionIdentification] = Field(
        None,
        description="Instructing Reimbursement Agent"
    )
    InstdRmbrsmntAgt: Optional[BranchAndFinancialInstitutionIdentification] = Field(
        None,
        description="Instructed Reimbursement Agent"
    )


class RemittanceInformation(BaseModel):
    """Remittance Information - RemittanceInformation16"""
    Ustrd: Optional[List[str]] = Field(
        None,
        description="Unstructured Remittance Information",
        max_length=140
    )


# ============================================================================
# Credit Transfer Transaction Information
# ============================================================================

class CreditTransferTransaction(BaseModel):
    """
    Credit Transfer Transaction Information - CreditTransferTransaction39
    
    Contains details of individual credit transfer transactions.
    """
    PmtId: PaymentIdentification = Field(
        ...,
        description="Payment Identification"
    )
    PmtTpInf: Optional[PaymentTypeInformation] = Field(
        None,
        description="Payment Type Information"
    )
    IntrBkSttlmAmt: ActiveOrHistoricCurrencyAndAmount = Field(
        ...,
        description="Interbank Settlement Amount"
    )
    IntrBkSttlmDt: Optional[str] = Field(
        None,
        description="Interbank Settlement Date (YYYY-MM-DD)"
    )
    AccptncDtTm: Optional[datetime] = Field(
        None,
        description="Acceptance Date Time"
    )
    ChrgBr: ChargeBearer = Field(
        ...,
        description="Charge Bearer Code"
    )
    InstgAgt: Optional[BranchAndFinancialInstitutionIdentification] = Field(
        None,
        description="Instructing Agent"
    )
    InstdAgt: Optional[BranchAndFinancialInstitutionIdentification] = Field(
        None,
        description="Instructed Agent"
    )
    Dbtr: Party = Field(
        ...,
        description="Debtor (Ordering Customer)"
    )
    DbtrAcct: Optional[CashAccount] = Field(
        None,
        description="Debtor Account"
    )
    DbtrAgt: Optional[BranchAndFinancialInstitutionIdentification] = Field(
        None,
        description="Debtor Agent"
    )
    CdtrAgt: Optional[BranchAndFinancialInstitutionIdentification] = Field(
        None,
        description="Creditor Agent"
    )
    Cdtr: Party = Field(
        ...,
        description="Creditor (Beneficiary Customer)"
    )
    CdtrAcct: Optional[CashAccount] = Field(
        None,
        description="Creditor Account"
    )
    RmtInf: Optional[RemittanceInformation] = Field(
        None,
        description="Remittance Information"
    )


# ============================================================================
# Group Header
# ============================================================================

class GroupHeader(BaseModel):
    """
    Group Header - GroupHeader93
    
    Set of characteristics shared by all individual transactions included in the message.
    """
    MsgId: str = Field(
        ...,
        description="Message Identification - Unique identifier for the message",
        max_length=35
    )
    CreDtTm: datetime = Field(
        ...,
        description="Creation Date Time - Date and time at which the message was created"
    )
    NbOfTxs: str = Field(
        ...,
        description="Number of Transactions - Total number of individual transactions",
        pattern=r"^\d{1,15}$"
    )
    SttlmInf: SettlementInstruction = Field(
        ...,
        description="Settlement Information"
    )
    InstgAgt: Optional[BranchAndFinancialInstitutionIdentification] = Field(
        None,
        description="Instructing Agent"
    )
    InstdAgt: Optional[BranchAndFinancialInstitutionIdentification] = Field(
        None,
        description="Instructed Agent"
    )


# ============================================================================
# FIToFI Customer Credit Transfer
# ============================================================================

class FIToFICustomerCreditTransfer(BaseModel):
    """
    FIToFI Customer Credit Transfer - FIToFICustomerCreditTransferV08
    
    The main message structure for pacs.008.001.08
    """
    GrpHdr: GroupHeader = Field(
        ...,
        description="Group Header - Common information for all transactions"
    )
    CdtTrfTxInf: List[CreditTransferTransaction] = Field(
        ...,
        description="Credit Transfer Transaction Information - Individual transaction details",
        min_length=1
    )


# ============================================================================
# Document Root
# ============================================================================

class Pacs008Document(BaseModel):
    """
    Document - ISO 20022 pacs.008.001.08 Root Element
    
    This is the top-level container for the FIToFICustomerCreditTransfer message.
    """
    Document: dict = Field(
        ...,
        description="Document wrapper containing FIToFICstmrCdtTrf"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "Document": {
                    "FIToFICstmrCdtTrf": {
                        "GrpHdr": {
                            "MsgId": "MSGID0001",
                            "CreDtTm": "2023-10-05T10:30:00",
                            "NbOfTxs": "1",
                            "SttlmInf": {
                                "SttlmMtd": "INDA"
                            }
                        },
                        "CdtTrfTxInf": []
                    }
                }
            }
        }


class Pacs008Message(BaseModel):
    """
    Complete pacs.008.001.08 message structure for easier programmatic access.
    
    This is a convenience model that unwraps the Document structure.
    """
    FIToFICstmrCdtTrf: FIToFICustomerCreditTransfer = Field(
        ...,
        description="FI To FI Customer Credit Transfer message"
    )


# ============================================================================
# Response Models
# ============================================================================

class ConversionResponse(BaseModel):
    """Response model for MT103 to pacs.008 conversion"""
    success: bool = Field(..., description="Conversion success status")
    pacs008_xml: Optional[str] = Field(None, description="Generated pacs.008 XML message")
    errors: Optional[List[str]] = Field(None, description="List of validation or conversion errors")
    warnings: Optional[List[str]] = Field(None, description="List of warnings")
    input_hash: str = Field(..., description="Hash of input message for logging")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Conversion timestamp")


class ConversionLog(BaseModel):
    """Model for logging conversion attempts"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    input_hash: str = Field(..., description="SHA256 hash of input (anonymized)")
    success: bool = Field(..., description="Whether conversion succeeded")
    errors: Optional[List[str]] = Field(None, description="List of errors if any")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
