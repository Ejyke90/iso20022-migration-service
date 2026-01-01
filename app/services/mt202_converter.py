"""
MT202 to pacs.009 Converter Service
Handles parsing of MT202 messages (Financial Institution Transfer) and conversion to ISO 20022 pacs.009.001.08 format
"""

import re
import hashlib
import xmltodict
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional, Tuple

from app.models.pacs009 import (
    Pacs009Document,
    FinancialInstitutionCreditTransfer,
    GroupHeader,
    FinancialInstitutionCreditTransferInstruction,
    FinancialInstitutionIdentification,
    BranchAndFinancialInstitutionIdentification,
    PaymentIdentification,
    ActiveCurrencyAndAmount,
    SettlementInstruction,
    RemittanceInformation,
    ChargeBearerType,
    InstructionForCreditorAgent,
)


# Custom Exceptions
class MT202ParseError(Exception):
    """Base exception for MT202 parsing errors"""
    pass


class MT202MissingFieldError(MT202ParseError):
    """Raised when a mandatory field is missing"""
    pass


class MT202ValidationError(MT202ParseError):
    """Raised when field validation fails"""
    pass


class Pacs009ConversionError(Exception):
    """Raised when conversion to pacs.009 fails"""
    pass


class MT202Parser:
    """Parser for MT202 SWIFT messages"""
    
    # Field patterns
    FIELD_PATTERNS = {
        'transaction_ref': r':20:([^\n:]+)',  # Sender's Reference
        'related_ref': r':21:([^\n:]+)',  # Related Reference (optional)
        'value_date': r':32A:(\d{6})',  # Value Date (YYMMDD)
        'currency_amount': r':32A:\d{6}([A-Z]{3})([\d,\.]+)',  # Currency and Amount
        'ordering_institution': r':52[AD]:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:)',  # Ordering Institution
        'senders_correspondent': r':53[ABD]:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:)',  # Sender's Correspondent
        'receivers_correspondent': r':54[ABD]:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:)',  # Receiver's Correspondent
        'intermediary': r':56[ACD]:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:)',  # Intermediary Institution
        'account_with_institution': r':57[ABCD]:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:)',  # Account With Institution
        'beneficiary_institution': r':58[AD]:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:)',  # Beneficiary Institution
        'sender_to_receiver_info': r':72:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:|$)',  # Sender to Receiver Information
    }
    
    @staticmethod
    def parse(mt202_message: str) -> Dict:
        """
        Parse MT202 message into structured dictionary
        
        Args:
            mt202_message: Raw MT202 SWIFT message text
            
        Returns:
            Dictionary with parsed fields
            
        Raises:
            MT202MissingFieldError: If mandatory fields are missing
            MT202ValidationError: If field validation fails
        """
        parsed = {}
        
        # Extract mandatory fields
        mandatory_fields = [
            ('transaction_ref', ':20:'),
            ('currency_amount', ':32A:'),
            ('ordering_institution', ':52'),
            ('beneficiary_institution', ':58'),
        ]
        
        for field_name, field_code in mandatory_fields:
            pattern = MT202Parser.FIELD_PATTERNS.get(field_name)
            if pattern:
                match = re.search(pattern, mt202_message, re.MULTILINE | re.DOTALL)
                if not match:
                    raise MT202MissingFieldError(
                        f"Mandatory field {field_code} not found in MT202 message"
                    )
                if field_name == 'currency_amount':
                    parsed['currency'] = match.group(1)
                    parsed['amount'] = match.group(2)
                else:
                    parsed[field_name] = match.group(1).strip()
        
        # Extract optional fields
        optional_fields = [
            'related_ref', 'value_date', 'senders_correspondent', 'receivers_correspondent',
            'intermediary', 'account_with_institution', 'sender_to_receiver_info'
        ]
        
        for field_name in optional_fields:
            pattern = MT202Parser.FIELD_PATTERNS.get(field_name)
            if pattern:
                match = re.search(pattern, mt202_message, re.MULTILINE | re.DOTALL)
                if match:
                    parsed[field_name] = match.group(1).strip()
        
        return parsed
    
    @staticmethod
    def parse_institution_info(institution_text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse institution information into BIC and name
        
        Returns:
            Tuple of (bic, name)
        """
        lines = [line.strip() for line in institution_text.split('\n') if line.strip()]
        
        bic = None
        name = None
        
        if lines:
            # First line is typically BIC or account number
            first_line = lines[0]
            # BIC pattern: 8 or 11 alphanumeric characters
            if re.match(r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$', first_line):
                bic = first_line
                name = ' '.join(lines[1:]) if len(lines) > 1 else None
            else:
                # If not BIC, treat as account/name
                if first_line.startswith('/'):
                    # Account number, next line is name
                    name = ' '.join(lines[1:]) if len(lines) > 1 else None
                else:
                    name = ' '.join(lines)
        
        return bic, name


class Pacs009Mapper:
    """Maps parsed MT202 data to pacs.009 structure"""
    
    @staticmethod
    def map_to_pacs009(parsed_data: Dict) -> Pacs009Document:
        """
        Map parsed MT202 data to pacs.009 document structure
        
        Args:
            parsed_data: Dictionary from MT202Parser.parse()
            
        Returns:
            Pacs009Document instance
            
        Raises:
            Pacs009ConversionError: If mapping fails
        """
        try:
            # Parse ordering institution
            ordering_bic, ordering_name = MT202Parser.parse_institution_info(
                parsed_data.get('ordering_institution', '')
            )
            
            # Parse beneficiary institution
            beneficiary_bic, beneficiary_name = MT202Parser.parse_institution_info(
                parsed_data.get('beneficiary_institution', '')
            )
            
            # Parse intermediary if present
            intermediary_bic = None
            intermediary_name = None
            if 'intermediary' in parsed_data:
                intermediary_bic, intermediary_name = MT202Parser.parse_institution_info(
                    parsed_data['intermediary']
                )
            
            # Create settlement instruction
            settlement_instruction = SettlementInstruction(
                SttlmMtd='INDA'  # Instructed Agent (default for MT202)
            )
            
            # Create group header
            group_header = GroupHeader(
                MsgId=f"MSG{parsed_data['transaction_ref'][:30]}",
                CreDtTm=datetime.utcnow(),
                NbOfTxs="1",  # MT202 is always single transaction
                SttlmInf=settlement_instruction,
                InstgAgt=BranchAndFinancialInstitutionIdentification(
                    FinInstnId=FinancialInstitutionIdentification(
                        BICFI=ordering_bic,
                        Nm=ordering_name
                    )
                ) if ordering_bic or ordering_name else None,
                InstdAgt=None
            )
            
            # Create payment identification
            payment_id = PaymentIdentification(
                InstrId=None,
                EndToEndId=parsed_data.get('related_ref', parsed_data['transaction_ref'])[:35],
                TxId=parsed_data['transaction_ref'][:35]
            )
            
            # Create interbank settlement amount
            amount_str = parsed_data['amount'].replace(',', '')
            interbank_amount = ActiveCurrencyAndAmount(
                Ccy=parsed_data['currency'],
                value=Decimal(amount_str)
            )
            
            # Create creditor agent (beneficiary institution)
            creditor_agent = BranchAndFinancialInstitutionIdentification(
                FinInstnId=FinancialInstitutionIdentification(
                    BICFI=beneficiary_bic,
                    Nm=beneficiary_name
                )
            )
            
            # Create intermediary agent if present
            intermediary_agent = None
            if intermediary_bic or intermediary_name:
                intermediary_agent = BranchAndFinancialInstitutionIdentification(
                    FinInstnId=FinancialInstitutionIdentification(
                        BICFI=intermediary_bic,
                        Nm=intermediary_name
                    )
                )
            
            # Create remittance information
            remittance_info = None
            if 'sender_to_receiver_info' in parsed_data:
                remittance_info = RemittanceInformation(
                    Ustrd=[parsed_data['sender_to_receiver_info'][:140]]
                )
            
            # Create credit transfer instruction
            credit_transfer = FinancialInstitutionCreditTransferInstruction(
                PmtId=payment_id,
                IntrBkSttlmAmt=interbank_amount,
                IntrBkSttlmDt=Pacs009Mapper._parse_value_date(parsed_data.get('value_date', '')),
                ChrgBr=ChargeBearerType.SHAR,  # Default for MT202
                InstgAgt=BranchAndFinancialInstitutionIdentification(
                    FinInstnId=FinancialInstitutionIdentification(
                        BICFI=ordering_bic,
                        Nm=ordering_name
                    )
                ) if ordering_bic or ordering_name else None,
                InstdAgt=None,
                IntrmyAgt1=intermediary_agent,
                CdtrAgt=creditor_agent,
                Cdtr=creditor_agent,  # In MT202, creditor is same as creditor agent
                RmtInf=remittance_info
            )
            
            # Create root document
            pacs009_doc = Pacs009Document(
                FICdtTrf=FinancialInstitutionCreditTransfer(
                    GrpHdr=group_header,
                    CdtTrfTxInf=[credit_transfer]
                )
            )
            
            return pacs009_doc
            
        except Exception as e:
            raise Pacs009ConversionError(f"Failed to map MT202 to pacs.009: {str(e)}")
    
    @staticmethod
    def _parse_value_date(date_str: str) -> Optional[str]:
        """Parse YYMMDD to ISO date format"""
        try:
            if date_str:
                dt = datetime.strptime(date_str, '%y%m%d')
                return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass
        return None


class XMLGenerator:
    """Generates pacs.009 XML from Pydantic model"""
    
    @staticmethod
    def pacs009_to_xml(pacs009_doc: Pacs009Document) -> str:
        """
        Convert pacs.009 document to XML string
        
        Args:
            pacs009_doc: Pacs009Document instance
            
        Returns:
            Formatted XML string with namespaces
        """
        # Convert to dictionary
        doc_dict = pacs009_doc.model_dump(exclude_none=True, by_alias=False)
        
        # Wrap in Document root with namespaces
        xml_dict = {
            'Document': {
                '@xmlns': 'urn:iso:std:iso:20022:tech:xsd:pacs.009.001.08',
                '@xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                **doc_dict
            }
        }
        
        # Convert to XML
        xml_output = xmltodict.unparse(
            xml_dict,
            pretty=True,
            indent='  '
        )
        
        return xml_output


def convert_mt202_to_pacs009(mt202_message: str) -> Tuple[str, str]:
    """
    Main conversion function: MT202 -> pacs.009 XML
    
    Args:
        mt202_message: Raw MT202 SWIFT message
        
    Returns:
        Tuple of (xml_output, input_hash)
        
    Raises:
        MT202ParseError: If parsing fails
        Pacs009ConversionError: If conversion fails
    """
    # Parse MT202
    parsed_data = MT202Parser.parse(mt202_message)
    
    # Map to pacs.009
    pacs009_doc = Pacs009Mapper.map_to_pacs009(parsed_data)
    
    # Generate XML
    xml_output = XMLGenerator.pacs009_to_xml(pacs009_doc)
    
    # Compute input hash for logging
    input_hash = hashlib.sha256(mt202_message.encode()).hexdigest()
    
    return xml_output, input_hash


def compute_input_hash(mt202_message: str) -> str:
    """Compute SHA256 hash of input for anonymized logging"""
    return hashlib.sha256(mt202_message.encode()).hexdigest()
