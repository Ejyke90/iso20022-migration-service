"""
MT103 to ISO 20022 pacs.008.001.08 Converter Service

This module handles the parsing of MT103 SWIFT messages and conversion
to ISO 20022 pacs.008 XML format.
"""

import re
import hashlib
import xmltodict
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Optional, List, Tuple
from xml.dom import minidom

from app.models import (
    MT103Message,
    Pacs008Message,
    FIToFICustomerCreditTransfer,
    GroupHeader,
    CreditTransferTransaction,
    PaymentIdentification,
    ActiveOrHistoricCurrencyAndAmount,
    Party,
    PostalAddress,
    CashAccount,
    AccountIdentificationOther,
    AccountIdentification,
    BranchAndFinancialInstitutionIdentification,
    FinancialInstitutionIdentification,
    SettlementInstruction,
    RemittanceInformation,
    ChargeBearer,
    SettlementMethod,
)


# ============================================================================
# Custom Exceptions
# ============================================================================

class MT103ParseError(Exception):
    """Raised when MT103 message cannot be parsed"""
    pass


class MT103MissingFieldError(MT103ParseError):
    """Raised when a mandatory MT103 field is missing"""
    def __init__(self, field_name: str):
        self.field_name = field_name
        super().__init__(f"Mandatory field '{field_name}' is missing from MT103 message")


class MT103ValidationError(MT103ParseError):
    """Raised when MT103 field validation fails"""
    pass


class ISO20022ConversionError(Exception):
    """Raised when conversion to ISO 20022 fails"""
    pass


# ============================================================================
# MT103 Field Parser
# ============================================================================

class MT103Parser:
    """
    Parser for SWIFT MT103 messages.
    
    Extracts structured data from raw MT103 text blocks.
    """
    
    # Regex patterns for MT103 fields
    PATTERNS = {
        'transaction_ref': r':20:([^\n:]+)',           # Transaction Reference (:20:) - MANDATORY
        'bank_operation_code': r':23B:([A-Z]{4})',     # Bank Operation Code (:23B:) - MANDATORY
        'instruction_code': r':23E:([^\n:]+)',         # Instruction Code (:23E:)
        'transaction_type_code': r':26T:([^\n:]+)',    # Transaction Type Code (:26T:)
        'value_date_currency_amount': r':32A:(\d{6})([A-Z]{3})([\d,\.]+)',  # Date, Currency, Amount (:32A:) - MANDATORY
        'currency_instructed_amount': r':33B:([A-Z]{3})([\d,\.]+)',  # Currency/Instructed Amount (:33B:)
        'exchange_rate': r':36:([\d\.]+)',             # Exchange Rate (:36:)
        'ordering_customer': r':50K:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:|$)',  # Ordering Customer (:50K:) - MANDATORY
        'ordering_institution': r':52[AD]?:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:|$)',  # Ordering Institution (:52:)
        'sender_correspondent': r':53[ABD]?:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:|$)',  # Sender's Correspondent (:53:)
        'receiver_correspondent': r':54[ABD]?:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:|$)',  # Receiver's Correspondent (:54:)
        'intermediary': r':56[ACD]?:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:|$)',  # Intermediary (:56:)
        'account_with': r':57[ABCD]?:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:|$)',  # Account With Institution (:57:)
        'beneficiary_customer': r':59:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:|$)',  # Beneficiary (:59:) - MANDATORY
        'remittance_info': r':70:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:|$)',  # Remittance Information (:70:)
        'details_of_charges': r':71A:([A-Z]{3})',      # Charge Bearer (:71A:) - MANDATORY
        'sender_charges': r':71F:([A-Z]{3})([\d,\.]+)',  # Sender's Charges (:71F:)
        'receiver_charges': r':71G:([A-Z]{3})([\d,\.]+)',  # Receiver's Charges (:71G:)
        'sender_to_receiver_info': r':72:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:|$)',  # Sender to Receiver Info (:72:)
    }
    
    @staticmethod
    def parse(mt103_text: str) -> Dict[str, any]:
        """
        Parse MT103 message text and extract fields.
        
        Args:
            mt103_text: Raw MT103 message text
            
        Returns:
            Dictionary containing parsed MT103 fields
            
        Raises:
            MT103MissingFieldError: If mandatory fields are missing
            MT103ParseError: If parsing fails
        """
        if not mt103_text or not mt103_text.strip():
            raise MT103ParseError("Empty MT103 message")
        
        parsed = {}
        
        # Extract transaction reference (:20:) - MANDATORY
        match = re.search(MT103Parser.PATTERNS['transaction_ref'], mt103_text)
        if not match:
            raise MT103MissingFieldError(':20: (Transaction Reference)')
        parsed['transaction_ref'] = match.group(1).strip()
        
        # Extract bank operation code (:23B:) - MANDATORY
        match = re.search(MT103Parser.PATTERNS['bank_operation_code'], mt103_text)
        if match:
            parsed['bank_operation_code'] = match.group(1).strip()
        
        # Extract instruction code (:23E:) - OPTIONAL
        match = re.search(MT103Parser.PATTERNS['instruction_code'], mt103_text)
        if match:
            parsed['instruction_code'] = match.group(1).strip()
        
        # Extract transaction type code (:26T:) - OPTIONAL
        match = re.search(MT103Parser.PATTERNS['transaction_type_code'], mt103_text)
        if match:
            parsed['transaction_type_code'] = match.group(1).strip()
        
        # Extract value date, currency, and amount (:32A:) - MANDATORY
        match = re.search(MT103Parser.PATTERNS['value_date_currency_amount'], mt103_text)
        if not match:
            raise MT103MissingFieldError(':32A: (Value Date, Currency, Amount)')
        
        value_date_str = match.group(1)  # YYMMDD
        
        # Extract currency/instructed amount (:33B:) - OPTIONAL
        match = re.search(MT103Parser.PATTERNS['currency_instructed_amount'], mt103_text)
        if match:
            instd_currency = match.group(1)
            instd_amount_str = match.group(2).replace(',', '')
            try:
                parsed['instructed_amount'] = Decimal(instd_amount_str)
                parsed['instructed_currency'] = instd_currency
            except (ValueError, TypeError):
                pass  # Optional field, ignore errors
        
        # Extract exchange rate (:36:) - OPTIONAL
        match = re.search(MT103Parser.PATTERNS['exchange_rate'], mt103_text)
        if match:
            try:
                parsed['exchange_rate'] = Decimal(match.group(1))
            except (ValueError, TypeError):
                pass  # Optional field, ignore errors
        parsed['currency'] = match.group(2)
        amount_str = match.group(3).replace(',', '')  # Remove comma separator
        
        try:
            parsed['amount'] = Decimal(amount_str)
            if parsed['amount'] <= 0:
                raise MT103ValidationError("Amount must be positive")
        except (ValueError, TypeError) as e:
            raise MT103ValidationError(f"Invalid amount format: {amount_str}") from e
        
        # Parse value date (YYMMDD to YYYY-MM-DD)
        try:
            parsed['value_date'] = MT103Parser._parse_date(value_date_str)
        except ValueError as e:
            raise MT103ValidationError(f"Invalid date format: {value_date_str}") from e
        
        # Extract orderin - Financial Institutions
        match = re.search(MT103Parser.PATTERNS['ordering_institution'], mt103_text)
        if match:
            parsed['ordering_institution'] = match.group(1).strip()
        
        match = re.search(MT103Parser.PATTERNS['sender_correspondent'], mt103_text)
        if match:
            parsed['sender_correspondent'] = match.group(1).strip()
        
        match = re.search(MT103Parser.PATTERNS['receiver_correspondent'], mt103_text)
        if match:
            parsed['receiver_correspondent'] = match.group(1).strip()
        
        match = re.search(MT103Parser.PATTERNS['intermediary'], mt103_text)
        if match:
            parsed['intermediary'] = match.group(1).strip()
        
        match = re.search(MT103Parser.PATTERNS['account_with'], mt103_text)
        if match:
            parsed['account_with'] = match.group(1).strip()
        
        # Optional fields - Payment Details
        match = re.search(MT103Parser.PATTERNS['remittance_info'], mt103_text)
        if match:
            parsed['remittance_info'] = match.group(1).strip()
        
        match = re.search(MT103Parser.PATTERNS['sender_charges'], mt103_text)
        if match:
            try:
                parsed['sender_charges_ccy'] = match.group(1)
                parsed['sender_charges_amount'] = Decimal(match.group(2).replace(',', ''))
            except (ValueError, TypeError):
                pass
        
        match = re.search(MT103Parser.PATTERNS['receiver_charges'], mt103_text)
        if match:
            try:
                parsed['receiver_charges_ccy'] = match.group(1)
                parsed['receiver_charges_amount'] = Decimal(match.group(2).replace(',', ''))
            except (ValueError, TypeError):
                pass
        
        match = re.search(MT103Parser.PATTERNS['sender_to_receiver_info'], mt103_text)
        if match:
            parsed['sender_to_receiver_info'] = match.group(1).strip()
        
        match = re.search(MT103Parser.PATTERNS['sender_correspondent'], mt103_text)
        if match:
            parsed['sender_correspondent'] = match.group(1).strip()
        
        match = re.search(MT103Parser.PATTERNS['receiver_correspondent'], mt103_text)
        if match:
            parsed['receiver_correspondent'] = match.group(1).strip()
        
        match = re.search(MT103Parser.PATTERNS['intermediary'], mt103_text)
        if match:
            parsed['intermediary'] = match.group(1).strip()
        
        match = re.search(MT103Parser.PATTERNS['account_with'], mt103_text)
        if match:
            parsed['account_with'] = match.group(1).strip()
        
        match = re.search(MT103Parser.PATTERNS['remittance_info'], mt103_text)
        if match:
            parsed['remittance_info'] = match.group(1).strip()
        
        return parsed
    
    @staticmethod
    def _parse_date(date_str: str) -> str:
        """
        Convert SWIFT date format (YYMMDD) to ISO format (YYYY-MM-DD).
        
        Args:
            date_str: Date in YYMMDD format
            
        Returns:
            Date in YYYY-MM-DD format
        """
        if len(date_str) != 6:
            raise ValueError(f"Invalid date format: {date_str}")
        
        yy = int(date_str[0:2])
        mm = int(date_str[2:4])
        dd = int(date_str[4:6])
        
        # Assume 20xx for years 00-49, 19xx for 50-99
        yyyy = 2000 + yy if yy < 50 else 1900 + yy
        
        # Validate the date
        date_obj = date(yyyy, mm, dd)
        return date_obj.isoformat()
    
    @staticmethod
    def _map_charge_bearer(mt_code: str) -> ChargeBearer:
        """
        Map MT103 charge code to ISO 20022 ChargeBearer.
        
        MT103 codes:
        - OUR: All charges are borne by the ordering customer
        - BEN: All charges are borne by the beneficiary
        - SHA: Charges are shared
        
        Args:
            mt_code: MT103 charge code (OUR/BEN/SHA)
            
        Returns:
            ISO 20022 ChargeBearer enum value
        """
        mapping = {
            'OUR': ChargeBearer.DEBT,  # Debtor (ordering customer) bears charges
            'BEN': ChargeBearer.CRED,  # Creditor (beneficiary) bears charges
            'SHA': ChargeBearer.SHAR,  # Shared charges
        }
        
        if mt_code not in mapping:
            raise MT103ValidationError(f"Invalid charge bearer code: {mt_code}")
        
        return mapping[mt_code]
    
    @staticmethod
    def parse_party_info(party_text: str) -> Tuple[Optional[str], Optional[str], List[str]]:
        """
        Parse party information from :50K: or :59: fields.
        
        Format:
        Line 1: Account number (optional, starts with /)
        Line 2+: Name and address
        
        Args:
            party_text: Raw party text from MT103
            
        Returns:
            Tuple of (account_number, name, address_lines)
        """
        lines = [line.strip() for line in party_text.split('\n') if line.strip()]
        
        if not lines:
            return None, None, []
        
        account_number = None
        name = None
        address_lines = []
        
        # Check if first line is account number (starts with /)
        if lines[0].startswith('/'):
            account_number = lines[0][1:]  # Remove leading /
            lines = lines[1:]
        
        # First remaining line is name
        if lines:
            name = lines[0]
            address_lines = lines[1:] if len(lines) > 1 else []
        
        return account_number, name, address_lines


# ============================================================================
# ISO 20022 Mapper
# ============================================================================

class ISO20022Mapper:
    """
    Maps parsed MT103 data to ISO 20022 pacs.008 structure.
    """
    
    @staticmethod
    def map_to_pacs008(parsed_mt103: Dict[str, any]) -> Pacs008Message:
        """
        Map parsed MT103 data to pacs.008 Pydantic model.
        
        Args:
            parsed_mt103: Dictionary of parsed MT103 fields
            
        Returns:
            Pacs008Message Pydantic model
            
        Raises:
            ISO20022ConversionError: If mapping fails
        """
        try:
            # Generate unique message ID
            msg_id = ISO20022Mapper._generate_message_id(parsed_mt103['transaction_ref'])
            
            # Parse ordering customer (debtor)
            debtor_account, debtor_name, debtor_address = MT103Parser.parse_party_info(
                parsed_mt103['ordering_customer']
            )
            
            # Parse beneficiary customer (creditor)
            creditor_account, creditor_name, creditor_address = MT103Parser.parse_party_info(
                parsed_mt103['beneficiary_customer']
            )
            
            # Build Debtor (Ordering Customer)
            debtor = Party(
                Nm=debtor_name or "UNKNOWN",
                PstlAdr=PostalAddress(AdrLine=debtor_address) if debtor_address else None
            )
            
            # Build Creditor (Beneficiary Customer)
            creditor = Party(
                Nm=creditor_name or "UNKNOWN",
                PstlAdr=PostalAddress(AdrLine=creditor_address) if creditor_address else None
            )
            
            # Build Debtor Account
            debtor_acct = None
            if debtor_account:
                debtor_acct = CashAccount(
                    Id=AccountIdentificationOther(
                        Othr=AccountIdentification(Id=debtor_account)
                    ),
                    Ccy=parsed_mt103['currency']
                )
            
            # Build Creditor Account
            creditor_acct = None
            if creditor_account:
                creditor_acct = CashAccount(
                    Id=AccountIdentificationOther(
                        Othr=AccountIdentification(Id=creditor_account)
                    ),
                    Ccy=parsed_mt103['currency']
                )
            
            # Build Settlement Amount
            settlement_amount = ActiveOrHistoricCurrencyAndAmount(
                Ccy=parsed_mt103['currency'],
                value=parsed_mt103['amount']
            )
            
            # Build Payment Identification
            payment_id = PaymentIdentification(
                InstrId=parsed_mt103['transaction_ref'],
                EndToEndId=parsed_mt103['transaction_ref'],
                TxId=msg_id
            )
            
            # Build Remittance Information (if available)
            remittance_info = None
            if 'remittance_info' in parsed_mt103:
                remittance_info = RemittanceInformation(
                    Ustrd=[parsed_mt103['remittance_info']]
                )
            
            # Build Credit Transfer Transaction
            credit_transfer_tx = CreditTransferTransaction(
                PmtId=payment_id,
                IntrBkSttlmAmt=settlement_amount,
                IntrBkSttlmDt=parsed_mt103['value_date'],
                ChrgBr=parsed_mt103['charge_bearer'],
                Dbtr=debtor,
                DbtrAcct=debtor_acct,
                Cdtr=creditor,
                CdtrAcct=creditor_acct,
                RmtInf=remittance_info
            )
            
            # Build Settlement Instruction
            settlement_info = SettlementInstruction(
                SttlmMtd=SettlementMethod.INDA
            )
            
            # Build Group Header
            group_header = GroupHeader(
                MsgId=msg_id,
                CreDtTm=datetime.utcnow(),
                NbOfTxs="1",
                SttlmInf=settlement_info
            )
            
            # Build FIToFI Customer Credit Transfer
            fi_to_fi_transfer = FIToFICustomerCreditTransfer(
                GrpHdr=group_header,
                CdtTrfTxInf=[credit_transfer_tx]
            )
            
            # Build Pacs008 Message
            pacs008_msg = Pacs008Message(
                FIToFICstmrCdtTrf=fi_to_fi_transfer
            )
            
            return pacs008_msg
            
        except Exception as e:
            raise ISO20022ConversionError(f"Failed to map MT103 to pacs.008: {str(e)}") from e
    
    @staticmethod
    def _generate_message_id(transaction_ref: str) -> str:
        """
        Generate a unique message ID based on transaction reference and timestamp.
        
        Args:
            transaction_ref: MT103 transaction reference
            
        Returns:
            Unique message ID (max 35 chars)
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        msg_id = f"{transaction_ref[:15]}_{timestamp}"
        return msg_id[:35]  # Ensure max 35 characters


# ============================================================================
# XML Generator
# ============================================================================

class XMLGenerator:
    """
    Converts Pydantic models to XML format.
    """
    
    @staticmethod
    def pacs008_to_xml(pacs008_msg: Pacs008Message, pretty: bool = True) -> str:
        """
        Convert pacs.008 Pydantic model to XML string.
        
        Args:
            pacs008_msg: Pacs008Message Pydantic model
            pretty: Whether to format XML with indentation
            
        Returns:
            XML string representation
        """
        # Convert Pydantic model to dictionary
        msg_dict = pacs008_msg.model_dump(by_alias=True, exclude_none=True)
        
        # Wrap in Document element
        document = {
            'Document': {
                '@xmlns': 'urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08',
                '@xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                **msg_dict
            }
        }
        
        # Convert to XML
        xml_str = xmltodict.unparse(document, pretty=pretty, indent='  ')
        
        # Format datetime values to ISO format
        xml_str = XMLGenerator._format_datetime_values(xml_str)
        
        return xml_str
    
    @staticmethod
    def _format_datetime_values(xml_str: str) -> str:
        """
        Ensure datetime values are properly formatted in XML.
        
        Args:
            xml_str: XML string
            
        Returns:
            XML string with formatted datetime values
        """
        # ISO 20022 requires datetime in format: YYYY-MM-DDTHH:MM:SS
        # This is already handled by Pydantic's datetime serialization
        return xml_str


# ============================================================================
# Main Conversion Function
# ============================================================================

def convert_mt103_to_iso(mt103_text: str) -> str:
    """
    Convert MT103 SWIFT message to ISO 20022 pacs.008.001.08 XML.
    
    This is the main entry point for the conversion service.
    
    Args:
        mt103_text: Raw MT103 message text
        
    Returns:
        ISO 20022 pacs.008 XML string
        
    Raises:
        MT103ParseError: If MT103 parsing fails
        MT103MissingFieldError: If mandatory fields are missing
        MT103ValidationError: If field validation fails
        ISO20022ConversionError: If ISO 20022 conversion fails
        
    Example:
        >>> mt103 = '''
        ... :20:TRF123456789
        ... :32A:231005USD10000,
        ... :50K:/1234567890
        ... JOHN DOE
        ... 123 MAIN ST
        ... NEW YORK, NY
        ... :59:/0987654321
        ... JANE SMITH
        ... 456 HIGH ST
        ... LONDON, UK
        ... :71A:OUR
        ... '''
        >>> xml = convert_mt103_to_iso(mt103)
    """
    # Step 1: Parse MT103 message
    parsed_mt103 = MT103Parser.parse(mt103_text)
    
    # Step 2: Map to ISO 20022 pacs.008 structure
    pacs008_msg = ISO20022Mapper.map_to_pacs008(parsed_mt103)
    
    # Step 3: Convert to XML
    xml_output = XMLGenerator.pacs008_to_xml(pacs008_msg, pretty=True)
    
    return xml_output


def compute_input_hash(mt103_text: str) -> str:
    """
    Compute SHA256 hash of input message for anonymized logging.
    
    Args:
        mt103_text: Raw MT103 message text
        
    Returns:
        SHA256 hash (hex string)
    """
    return hashlib.sha256(mt103_text.encode('utf-8')).hexdigest()
