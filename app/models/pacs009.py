"""
ISO 20022 pacs.009.001.08 Data Models (Financial Institution Credit Transfer)

This module defines Pydantic models for the pacs.009.001.08 schema used for
financial institution to financial institution credit transfers (MT202 equivalent).
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Enums
# ============================================================================

class ChargeBearerType(str, Enum):
    """Charge Bearer Type - ISO 20022 ChargeBearerType1Code"""
    DEBT = "DEBT"  # BorneByDebtor (OUR in MT messages)
    CRED = "CRED"  # BorneByCreditor (BEN in MT messages)
    SHAR = "SHAR"  # Shared (SHA in MT messages)
    SLEV = "SLEV"  # Service Level


# ============================================================================
# Core Models
# ============================================================================

class MT202Message(BaseModel):
    """Input model for MT202 message"""
    mt202_message: str = Field(
        ...,
        description="Raw MT202 SWIFT message text",
        min_length=10
    )


class ActiveCurrencyAndAmount(BaseModel):
    """Active Currency and Amount - ActiveCurrencyAndAmount"""
    Ccy: str = Field(..., description="Currency Code", min_length=3, max_length=3)
    value: Decimal = Field(..., description="Amount value", gt=0)

    class Config:
        json_encoders = {
            Decimal: lambda v: str(v)
        }


class FinancialInstitutionIdentification(BaseModel):
    """Financial Institution Identification - FinancialInstitutionIdentification18"""
    BICFI: Optional[str] = Field(None, description="BIC (Bank Identifier Code)", max_length=11)
    ClrSysMmbId: Optional[dict] = Field(None, description="Clearing System Member Identification")
    Nm: Optional[str] = Field(None, description="Institution Name", max_length=140)
    PstlAdr: Optional[dict] = Field(None, description="Postal Address")


class BranchAndFinancialInstitutionIdentification(BaseModel):
    """Branch and Financial Institution Identification - BranchAndFinancialInstitutionIdentification6"""
    FinInstnId: FinancialInstitutionIdentification = Field(
        ...,
        description="Financial Institution Identification"
    )


class PaymentIdentification(BaseModel):
    """Payment Identification - PaymentIdentification13"""
    InstrId: Optional[str] = Field(None, description="Instruction Identification", max_length=35)
    EndToEndId: str = Field(..., description="End-to-End Identification", max_length=35)
    TxId: str = Field(..., description="Transaction Identification", max_length=35)
    UETR: Optional[str] = Field(None, description="Unique End-to-End Transaction Reference", max_length=36)


class SettlementInstruction(BaseModel):
    """Settlement Instruction"""
    SttlmMtd: str = Field(..., description="Settlement Method (INDA/INGA/COVE)")
    InstgRmbrsmntAgt: Optional[BranchAndFinancialInstitutionIdentification] = Field(
        None,
        description="Instructing Reimbursement Agent"
    )
    InstdRmbrsmntAgt: Optional[BranchAndFinancialInstitutionIdentification] = Field(
        None,
        description="Instructed Reimbursement Agent"
    )


class GroupHeader(BaseModel):
    """Group Header - GroupHeader93"""
    MsgId: str = Field(..., description="Message Identification", max_length=35)
    CreDtTm: datetime = Field(..., description="Creation Date Time")
    NbOfTxs: str = Field(..., description="Number of Transactions")
    SttlmInf: SettlementInstruction = Field(..., description="Settlement Information")
    InstgAgt: Optional[BranchAndFinancialInstitutionIdentification] = Field(
        None,
        description="Instructing Agent"
    )
    InstdAgt: Optional[BranchAndFinancialInstitutionIdentification] = Field(
        None,
        description="Instructed Agent"
    )


class InstructionForCreditorAgent(BaseModel):
    """Instruction for Creditor Agent"""
    Cd: Optional[str] = Field(None, description="Instruction Code")
    InstrInf: Optional[str] = Field(None, description="Instruction Information", max_length=140)


class RemittanceInformation(BaseModel):
    """Remittance Information - RemittanceInformation16"""
    Ustrd: Optional[List[str]] = Field(
        None,
        description="Unstructured remittance information",
        max_length=4
    )
    
    @field_validator('Ustrd')
    @classmethod
    def validate_ustrd(cls, v):
        if v:
            # Ensure each line is max 140 characters
            return [line[:140] for line in v]
        return v


class FinancialInstitutionCreditTransferInstruction(BaseModel):
    """Financial Institution Credit Transfer Instruction - CreditTransferTransaction40"""
    PmtId: PaymentIdentification = Field(..., description="Payment Identification")
    IntrBkSttlmAmt: ActiveCurrencyAndAmount = Field(..., description="Interbank Settlement Amount")
    IntrBkSttlmDt: Optional[str] = Field(None, description="Interbank Settlement Date (YYYY-MM-DD)")
    ChrgBr: Optional[ChargeBearerType] = Field(None, description="Charge Bearer")
    InstgAgt: Optional[BranchAndFinancialInstitutionIdentification] = Field(
        None,
        description="Instructing Agent"
    )
    InstdAgt: Optional[BranchAndFinancialInstitutionIdentification] = Field(
        None,
        description="Instructed Agent"
    )
    IntrmyAgt1: Optional[BranchAndFinancialInstitutionIdentification] = Field(
        None,
        description="Intermediary Agent 1"
    )
    CdtrAgt: Optional[BranchAndFinancialInstitutionIdentification] = Field(
        None,
        description="Creditor Agent (Beneficiary Institution)"
    )
    Cdtr: Optional[BranchAndFinancialInstitutionIdentification] = Field(
        None,
        description="Creditor (Beneficiary Financial Institution)"
    )
    InstrForCdtrAgt: Optional[List[InstructionForCreditorAgent]] = Field(
        None,
        description="Instructions for Creditor Agent"
    )
    RmtInf: Optional[RemittanceInformation] = Field(None, description="Remittance Information")


class FinancialInstitutionCreditTransfer(BaseModel):
    """Financial Institution Credit Transfer - FIToFIPaymentStatusReportV10"""
    GrpHdr: GroupHeader = Field(..., description="Group Header")
    CdtTrfTxInf: List[FinancialInstitutionCreditTransferInstruction] = Field(
        ...,
        description="Credit Transfer Transaction Information"
    )


class Pacs009Document(BaseModel):
    """Root document for pacs.009.001.08"""
    FICdtTrf: FinancialInstitutionCreditTransfer = Field(
        ...,
        alias="FICdtTrf",
        description="Financial Institution Credit Transfer"
    )
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%dT%H:%M:%S'),
            Decimal: lambda v: str(v)
        }


class ConversionResponse(BaseModel):
    """Response model for MT202 conversion"""
    success: bool = Field(..., description="Whether conversion succeeded")
    message: Optional[str] = Field(None, description="Success or error message")
    pacs009_xml: Optional[str] = Field(None, description="Generated pacs.009 XML")
    errors: Optional[List[str]] = Field(None, description="List of errors if conversion failed")
    input_hash: Optional[str] = Field(None, description="SHA256 hash of input (anonymized)")
