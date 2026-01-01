"""
MT101 to pain.001 Converter Service
Handles parsing of MT101 messages and conversion to ISO 20022 pain.001.001.09 format
"""

import re
import hashlib
import xmltodict
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from app.models.pain001 import (
    Pain001Document,
    CustomerCreditTransferInitiation,
    GroupHeader,
    PaymentInstruction,
    CreditTransferTransactionInformation,
    Party,
    CashAccount,
    Agent,
    FinancialInstitution,
    PostalAddress,
    PaymentTypeInformation,
    RemittanceInformation,
    ChargeBearerType,
)


# Custom Exceptions
class MT101ParseError(Exception):
    """Base exception for MT101 parsing errors"""
    pass


class MT101MissingFieldError(MT101ParseError):
    """Raised when a mandatory field is missing"""
    pass


class MT101ValidationError(MT101ParseError):
    """Raised when field validation fails"""
    pass


class Pain001ConversionError(Exception):
    """Raised when conversion to pain.001 fails"""
    pass


class MT101Parser:
    """Parser for MT101 SWIFT messages"""
    
    # Field patterns
    FIELD_PATTERNS = {
        'transaction_ref': r':20:([^\n:]+)',  # Transaction Reference
        'value_date': r':30:(\d{6})',  # Value Date (YYMMDD)
        'currency_code': r':32B:([A-Z]{3})',  # Currency Code
        'total_amount': r':32B:[A-Z]{3}([\d,\.]+)',  # Total Sum
        'ordering_customer': r':50[KF]:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:)',  # Ordering Customer
        'ordering_institution': r':52[AD]:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:)',  # Ordering Institution
        'account_with_institution': r':57[ACD]:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:)',  # Account With Institution
        'beneficiary_customer': r':59:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:)',  # Beneficiary Customer
        'details_of_charges': r':71A:([A-Z]{3})',  # Details of Charges
        'instruction_code': r':23E:([A-Z]{4}(?:/[^\n]+)?)',  # Instruction Code
        'remittance_info': r':70:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:|$)',  # Remittance Information
    }
    
    # Transaction block pattern (for multiple transactions)
    TRANSACTION_PATTERN = r':21:([^\n:]+)'  # Transaction sequence number
    TRANSACTION_AMOUNT_PATTERN = r':32B:([A-Z]{3})([\d,\.]+)'  # Currency and amount per transaction
    
    @staticmethod
    def parse(mt101_message: str) -> Dict:
        """
        Parse MT101 message into structured dictionary
        
        Args:
            mt101_message: Raw MT101 SWIFT message text
            
        Returns:
            Dictionary with parsed fields
            
        Raises:
            MT101MissingFieldError: If mandatory fields are missing
            MT101ValidationError: If field validation fails
        """
        parsed = {}
        
        # Extract mandatory fields
        mandatory_fields = [
            ('transaction_ref', ':20:'),
            ('ordering_customer', ':50'),
            ('currency_code', ':32B:'),
        ]
        
        for field_name, field_code in mandatory_fields:
            pattern = MT101Parser.FIELD_PATTERNS.get(field_name)
            if pattern:
                match = re.search(pattern, mt101_message, re.MULTILINE | re.DOTALL)
                if not match:
                    raise MT101MissingFieldError(
                        f"Mandatory field {field_code} not found in MT101 message"
                    )
                parsed[field_name] = match.group(1).strip()
        
        # Extract optional fields
        optional_fields = [
            'value_date', 'total_amount', 'ordering_institution',
            'account_with_institution', 'details_of_charges',
            'instruction_code', 'remittance_info'
        ]
        
        for field_name in optional_fields:
            pattern = MT101Parser.FIELD_PATTERNS.get(field_name)
            if pattern:
                match = re.search(pattern, mt101_message, re.MULTILINE | re.DOTALL)
                if match:
                    parsed[field_name] = match.group(1).strip()
        
        # Parse multiple transactions
        parsed['transactions'] = MT101Parser._parse_transactions(mt101_message)
        
        return parsed
    
    @staticmethod
    def _parse_transactions(mt101_message: str) -> List[Dict]:
        """Parse individual transaction blocks from MT101"""
        transactions = []
        
        # Find all transaction sequence numbers
        transaction_matches = list(re.finditer(r':21:([^\n:]+)', mt101_message))
        
        if not transaction_matches:
            # Single transaction case - parse the whole message
            transaction = MT101Parser._parse_single_transaction(mt101_message)
            if transaction:
                transactions.append(transaction)
        else:
            # Multiple transactions - split by :21: markers
            for i, match in enumerate(transaction_matches):
                start_pos = match.start()
                end_pos = transaction_matches[i + 1].start() if i + 1 < len(transaction_matches) else len(mt101_message)
                transaction_block = mt101_message[start_pos:end_pos]
                
                transaction = MT101Parser._parse_single_transaction(transaction_block)
                if transaction:
                    transaction['sequence_number'] = match.group(1).strip()
                    transactions.append(transaction)
        
        return transactions
    
    @staticmethod
    def _parse_single_transaction(transaction_block: str) -> Optional[Dict]:
        """Parse a single transaction from MT101"""
        transaction = {}
        
        # Amount and currency
        amount_match = re.search(r':32B:([A-Z]{3})([\d,\.]+)', transaction_block)
        if amount_match:
            transaction['currency'] = amount_match.group(1)
            amount_str = amount_match.group(2).replace(',', '')
            transaction['amount'] = Decimal(amount_str)
        
        # Beneficiary customer (mandatory for each transaction)
        beneficiary_match = re.search(
            r':59:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:|$)',
            transaction_block,
            re.MULTILINE | re.DOTALL
        )
        if beneficiary_match:
            transaction['beneficiary'] = beneficiary_match.group(1).strip()
        
        # Beneficiary institution (optional)
        beneficiary_inst_match = re.search(
            r':57[ACD]:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:|$)',
            transaction_block,
            re.MULTILINE | re.DOTALL
        )
        if beneficiary_inst_match:
            transaction['beneficiary_institution'] = beneficiary_inst_match.group(1).strip()
        
        # Remittance information (optional)
        remit_match = re.search(
            r':70:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:|$)',
            transaction_block,
            re.MULTILINE | re.DOTALL
        )
        if remit_match:
            transaction['remittance_info'] = remit_match.group(1).strip()
        
        return transaction if transaction else None
    
    @staticmethod
    def parse_party_info(party_text: str) -> Tuple[Optional[str], Optional[str], Optional[List[str]]]:
        """
        Parse party information into account, name, and address
        
        Returns:
            Tuple of (account, name, address_lines)
        """
        lines = [line.strip() for line in party_text.split('\n') if line.strip()]
        
        account = None
        name = None
        address_lines = []
        
        if lines:
            # First line might be account (starts with /)
            if lines[0].startswith('/'):
                account = lines[0][1:]  # Remove leading /
                lines = lines[1:]
            
            # Next line(s) are name and address
            if lines:
                name = lines[0]
                address_lines = lines[1:] if len(lines) > 1 else []
        
        return account, name, address_lines


class Pain001Mapper:
    """Maps parsed MT101 data to pain.001 structure"""
    
    @staticmethod
    def map_to_pain001(parsed_data: Dict) -> Pain001Document:
        """
        Map parsed MT101 data to pain.001 document structure
        
        Args:
            parsed_data: Dictionary from MT101Parser.parse()
            
        Returns:
            Pain001Document instance
            
        Raises:
            Pain001ConversionError: If mapping fails
        """
        try:
            # Parse ordering customer
            ordering_account, ordering_name, ordering_address = MT101Parser.parse_party_info(
                parsed_data.get('ordering_customer', '')
            )
            
            # Parse ordering institution (debtor agent)
            ordering_inst_text = parsed_data.get('ordering_institution', '')
            ordering_inst_bic, ordering_inst_name, _ = MT101Parser.parse_party_info(ordering_inst_text)
            
            # Parse account with institution (if present)
            account_inst_text = parsed_data.get('account_with_institution', '')
            account_inst_bic = None
            if account_inst_text:
                account_inst_bic, _, _ = MT101Parser.parse_party_info(account_inst_text)
            
            # Create group header
            num_transactions = len(parsed_data['transactions'])
            group_header = GroupHeader(
                MsgId=f"MSG{parsed_data['transaction_ref'][:30]}",
                CreDtTm=datetime.utcnow(),
                NbOfTxs=str(num_transactions),
                InitgPty=Party(
                    Nm=ordering_name or "Unknown Initiator"
                )
            )
            
            # Map charge bearer
            charge_bearer = Pain001Mapper._map_charge_bearer(
                parsed_data.get('details_of_charges', 'SHA')
            )
            
            # Create payment instruction
            requested_execution_date = Pain001Mapper._parse_value_date(
                parsed_data.get('value_date', datetime.utcnow().strftime('%y%m%d'))
            )
            
            # Create credit transfer transactions
            credit_transfers = []
            for idx, txn in enumerate(parsed_data['transactions']):
                credit_transfer = Pain001Mapper._create_credit_transfer(
                    txn, idx, account_inst_bic, charge_bearer
                )
                credit_transfers.append(credit_transfer)
            
            # Create debtor agent
            debtor_agent = Agent(
                FinInstnId=FinancialInstitution(
                    BICFI=ordering_inst_bic if ordering_inst_bic and len(ordering_inst_bic) >= 8 else None,
                    Nm=ordering_inst_name
                )
            )
            
            payment_instruction = PaymentInstruction(
                PmtInfId=f"PMT{parsed_data['transaction_ref'][:30]}",
                PmtMtd="TRF",
                NbOfTxs=str(num_transactions),
                ReqdExctnDt={"Dt": requested_execution_date},
                Dbtr=Party(
                    Nm=ordering_name or "Unknown Debtor",
                    PstlAdr=PostalAddress(
                        AdrLine=ordering_address[:7] if ordering_address else None
                    ) if ordering_address else None
                ),
                DbtrAcct=CashAccount(
                    Id={"IBAN": ordering_account} if ordering_account and ordering_account.startswith(('GB', 'DE', 'FR', 'IT')) 
                        else {"Othr": {"Id": ordering_account or "UNKNOWN"}}
                ),
                DbtrAgt=debtor_agent,
                ChrgBr=charge_bearer,
                CdtTrfTxInf=credit_transfers
            )
            
            # Create root document
            pain001_doc = Pain001Document(
                CstmrCdtTrfInitn=CustomerCreditTransferInitiation(
                    GrpHdr=group_header,
                    PmtInf=[payment_instruction]
                )
            )
            
            return pain001_doc
            
        except Exception as e:
            raise Pain001ConversionError(f"Failed to map MT101 to pain.001: {str(e)}")
    
    @staticmethod
    def _create_credit_transfer(
        txn: Dict,
        index: int,
        creditor_agent_bic: Optional[str],
        charge_bearer: ChargeBearerType
    ) -> CreditTransferTransactionInformation:
        """Create a single credit transfer transaction"""
        
        # Parse beneficiary
        beneficiary_account, beneficiary_name, beneficiary_address = MT101Parser.parse_party_info(
            txn.get('beneficiary', '')
        )
        
        # Parse beneficiary institution if present
        creditor_bic = creditor_agent_bic
        creditor_name = None
        if 'beneficiary_institution' in txn:
            bic, name, _ = MT101Parser.parse_party_info(txn['beneficiary_institution'])
            if bic:
                creditor_bic = bic
            if name:
                creditor_name = name
        
        # Create creditor agent
        creditor_agent = None
        if creditor_bic or creditor_name:
            creditor_agent = Agent(
                FinInstnId=FinancialInstitution(
                    BICFI=creditor_bic if creditor_bic and len(creditor_bic) >= 8 else None,
                    Nm=creditor_name
                )
            )
        
        # Create remittance information
        remittance_info = None
        if 'remittance_info' in txn:
            remittance_info = RemittanceInformation(
                Ustrd=[txn['remittance_info'][:140]]
            )
        
        return CreditTransferTransactionInformation(
            PmtId={
                "InstrId": f"INSTR{index + 1:03d}",
                "EndToEndId": txn.get('sequence_number', f"E2E{index + 1:03d}")
            },
            Amt={
                "InstdAmt": {
                    "Ccy": txn.get('currency', 'USD'),
                    "value": str(txn.get('amount', Decimal('0')))
                }
            },
            ChrgBr=charge_bearer,
            CdtrAgt=creditor_agent,
            Cdtr=Party(
                Nm=beneficiary_name or "Unknown Beneficiary",
                PstlAdr=PostalAddress(
                    AdrLine=beneficiary_address[:7] if beneficiary_address else None
                ) if beneficiary_address else None
            ),
            CdtrAcct=CashAccount(
                Id={"IBAN": beneficiary_account} if beneficiary_account and beneficiary_account.startswith(('GB', 'DE', 'FR', 'IT'))
                    else {"Othr": {"Id": beneficiary_account or "UNKNOWN"}}
            ),
            RmtInf=remittance_info
        )
    
    @staticmethod
    def _map_charge_bearer(mt_charge_code: str) -> ChargeBearerType:
        """Map MT101 charge code to pain.001 charge bearer"""
        mapping = {
            'OUR': ChargeBearerType.DEBT,
            'BEN': ChargeBearerType.CRED,
            'SHA': ChargeBearerType.SHAR,
        }
        return mapping.get(mt_charge_code.upper(), ChargeBearerType.SHAR)
    
    @staticmethod
    def _parse_value_date(date_str: str) -> str:
        """Parse YYMMDD to ISO date format"""
        try:
            dt = datetime.strptime(date_str, '%y%m%d')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return datetime.utcnow().strftime('%Y-%m-%d')


class XMLGenerator:
    """Generates pain.001 XML from Pydantic model"""
    
    @staticmethod
    def pain001_to_xml(pain001_doc: Pain001Document) -> str:
        """
        Convert pain.001 document to XML string
        
        Args:
            pain001_doc: Pain001Document instance
            
        Returns:
            Formatted XML string with namespaces
        """
        # Convert to dictionary
        doc_dict = pain001_doc.model_dump(exclude_none=True, by_alias=False)
        
        # Wrap in Document root with namespaces
        xml_dict = {
            'Document': {
                '@xmlns': 'urn:iso:std:iso:20022:tech:xsd:pain.001.001.09',
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


def convert_mt101_to_pain001(mt101_message: str) -> Tuple[str, str]:
    """
    Main conversion function: MT101 -> pain.001 XML
    
    Args:
        mt101_message: Raw MT101 SWIFT message
        
    Returns:
        Tuple of (xml_output, input_hash)
        
    Raises:
        MT101ParseError: If parsing fails
        Pain001ConversionError: If conversion fails
    """
    # Parse MT101
    parsed_data = MT101Parser.parse(mt101_message)
    
    # Map to pain.001
    pain001_doc = Pain001Mapper.map_to_pain001(parsed_data)
    
    # Generate XML
    xml_output = XMLGenerator.pain001_to_xml(pain001_doc)
    
    # Compute input hash for logging
    input_hash = hashlib.sha256(mt101_message.encode()).hexdigest()
    
    return xml_output, input_hash


def compute_input_hash(mt101_message: str) -> str:
    """Compute SHA256 hash of input for anonymized logging"""
    return hashlib.sha256(mt101_message.encode()).hexdigest()
