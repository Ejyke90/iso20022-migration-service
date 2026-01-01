"""
ISO 20022 pain.001.001.09 (Customer Credit Transfer Initiation) models
Used for MT101 -> pain.001 conversion
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class ServiceLevel(str, Enum):
    """Service level codes"""
    SEPA = "SEPA"
    SDVA = "SDVA"
    PRPT = "PRPT"
    URGP = "URGP"


class LocalInstrument(str, Enum):
    """Local instrument codes"""
    INST = "INST"
    RTGS = "RTGS"


class ChargeBearerType(str, Enum):
    """Charge bearer type codes for pain.001"""
    DEBT = "DEBT"  # Borne by debtor
    CRED = "CRED"  # Borne by creditor
    SHAR = "SHAR"  # Shared
    SLEV = "SLEV"  # Service level


class PostalAddress(BaseModel):
    """Postal address information"""
    StrtNm: Optional[str] = Field(None, max_length=70)
    BldgNb: Optional[str] = Field(None, max_length=16)
    PstCd: Optional[str] = Field(None, max_length=16)
    TwnNm: Optional[str] = Field(None, max_length=35)
    CtrySubDvsn: Optional[str] = Field(None, max_length=35)
    Ctry: Optional[str] = Field(None, min_length=2, max_length=2)
    AdrLine: Optional[List[str]] = Field(None, max_items=7)


class Party(BaseModel):
    """Party identification"""
    Nm: Optional[str] = Field(None, max_length=140)
    PstlAdr: Optional[PostalAddress] = None
    Id: Optional[dict] = None


class CashAccount(BaseModel):
    """Cash account information"""
    Id: dict = Field(...)  # IBAN or Other
    Ccy: Optional[str] = Field(None, min_length=3, max_length=3)


class FinancialInstitution(BaseModel):
    """Financial institution identification"""
    BICFI: Optional[str] = Field(None, min_length=8, max_length=11)
    Nm: Optional[str] = Field(None, max_length=140)
    PstlAdr: Optional[PostalAddress] = None


class Agent(BaseModel):
    """Agent (bank) information"""
    FinInstnId: FinancialInstitution


class ActiveOrHistoricCurrencyAndAmount(BaseModel):
    """Amount with currency"""
    Ccy: str = Field(..., min_length=3, max_length=3)
    value: Decimal = Field(..., gt=0)

    @field_validator('value')
    @classmethod
    def validate_positive_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class PaymentTypeInformation(BaseModel):
    """Payment type information"""
    InstrPrty: Optional[str] = Field(None, pattern="^(HIGH|NORM)$")
    SvcLvl: Optional[dict] = None
    LclInstrm: Optional[dict] = None
    CtgyPurp: Optional[dict] = None


class RemittanceInformation(BaseModel):
    """Remittance information"""
    Ustrd: Optional[List[str]] = Field(None, max_items=1)
    Strd: Optional[dict] = None


class CreditTransferTransactionInformation(BaseModel):
    """Individual credit transfer transaction"""
    PmtId: dict = Field(...)  # InstrId, EndToEndId
    PmtTpInf: Optional[PaymentTypeInformation] = None
    Amt: dict = Field(...)  # InstdAmt
    ChrgBr: Optional[ChargeBearerType] = None
    CdtrAgt: Optional[Agent] = None
    Cdtr: Party = Field(...)
    CdtrAcct: CashAccount = Field(...)
    RmtInf: Optional[RemittanceInformation] = None
    Purp: Optional[dict] = None


class PaymentInstruction(BaseModel):
    """Payment instruction information"""
    PmtInfId: str = Field(..., max_length=35)
    PmtMtd: str = Field(default="TRF")  # Transfer
    BtchBookg: Optional[bool] = None
    NbOfTxs: str = Field(...)  # Number of transactions
    CtrlSum: Optional[Decimal] = None  # Control sum
    PmtTpInf: Optional[PaymentTypeInformation] = None
    ReqdExctnDt: dict = Field(...)  # Requested execution date
    Dbtr: Party = Field(...)  # Debtor
    DbtrAcct: CashAccount = Field(...)  # Debtor account
    DbtrAgt: Agent = Field(...)  # Debtor agent
    ChrgBr: Optional[ChargeBearerType] = None
    CdtTrfTxInf: List[CreditTransferTransactionInformation] = Field(...)


class GroupHeader(BaseModel):
    """Group header information"""
    MsgId: str = Field(..., max_length=35)
    CreDtTm: datetime = Field(default_factory=datetime.utcnow)
    NbOfTxs: str = Field(...)  # Total number of transactions
    CtrlSum: Optional[Decimal] = None  # Control sum
    InitgPty: Party = Field(...)  # Initiating party


class CustomerCreditTransferInitiation(BaseModel):
    """Main customer credit transfer initiation message"""
    GrpHdr: GroupHeader = Field(...)
    PmtInf: List[PaymentInstruction] = Field(..., min_items=1)


class Pain001Document(BaseModel):
    """Root pain.001.001.09 document"""
    CstmrCdtTrfInitn: CustomerCreditTransferInitiation = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "CstmrCdtTrfInitn": {
                    "GrpHdr": {
                        "MsgId": "MSG123456789",
                        "CreDtTm": "2023-10-05T10:30:00",
                        "NbOfTxs": "2",
                        "InitgPty": {
                            "Nm": "ACME Corporation"
                        }
                    },
                    "PmtInf": [{
                        "PmtInfId": "PMT123456789",
                        "PmtMtd": "TRF",
                        "NbOfTxs": "2",
                        "ReqdExctnDt": {"Dt": "2023-10-05"},
                        "Dbtr": {"Nm": "ACME Corporation"},
                        "DbtrAcct": {"Id": {"IBAN": "GB29NWBK60161331926819"}},
                        "DbtrAgt": {"FinInstnId": {"BICFI": "NWBKGB2L"}},
                        "CdtTrfTxInf": [{
                            "PmtId": {
                                "InstrId": "INSTR001",
                                "EndToEndId": "E2E001"
                            },
                            "Amt": {
                                "InstdAmt": {
                                    "Ccy": "EUR",
                                    "value": "10000.00"
                                }
                            },
                            "Cdtr": {"Nm": "Supplier Inc"},
                            "CdtrAcct": {"Id": {"IBAN": "DE89370400440532013000"}}
                        }]
                    }]
                }
            }
        }


class MT101Message(BaseModel):
    """Input model for MT101 message"""
    mt101_message: str = Field(..., description="Raw MT101 SWIFT message text")

    @field_validator('mt101_message')
    @classmethod
    def validate_mt101_format(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("MT101 message cannot be empty")
        if ':20:' not in v:  # Transaction reference must exist
            raise ValueError("MT101 message must contain :20: (Transaction Reference)")
        return v


class ConversionResponse(BaseModel):
    """API response model for MT101 conversion"""
    success: bool
    message: str
    pain001_xml: Optional[str] = None
    errors: Optional[List[str]] = None
    input_hash: Optional[str] = None
