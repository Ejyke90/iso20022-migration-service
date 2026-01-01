"""
MT102 to pacs.008 Converter Service
Handles parsing of MT102 messages (Multiple Customer Credit Transfer) and conversion to ISO 20022 pacs.008.001.08 format
"""

import re
import hashlib
import xmltodict
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from app.models.pacs008 import (
    Pacs008Document,
    FIToFICustomerCreditTransfer,
    GroupHeader,
    CreditTransferTransaction,
    Party,
    CashAccount,
    BranchAndFinancialInstitutionIdentification,
    FinancialInstitutionIdentification,
    PostalAddress,
    PaymentIdentification,
    ActiveOrHistoricCurrencyAndAmount,
    RemittanceInformation,
    ChargeBearer,
)


# Custom Exceptions
class MT102ParseError(Exception):
    """Base exception for MT102 parsing errors"""
    pass


class MT102MissingFieldError(MT102ParseError):
    """Raised when a mandatory field is missing"""
    pass


class MT102ValidationError(MT102ParseError):
    """Raised when field validation fails"""
    pass


class Pacs008ConversionError(Exception):
    """Raised when conversion to pacs.008 fails"""
    pass


class MT102Parser:
    """Parser for MT102 SWIFT messages"""
    
    # Field patterns
    FIELD_PATTERNS = {
        'transaction_ref': r':20:([^\n:]+)',  # Sender's Reference
        'value_date': r':32A:(\d{6})',  # Value Date (YYMMDD)
        'currency_amount': r':32A:\d{6}([A-Z]{3})([\d,\.]+)',  # Currency and Total Amount
        'ordering_customer': r':50[KF]:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:)',  # Ordering Customer
        'ordering_institution': r':52[AD]:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:)',  # Ordering Institution
        'account_with_institution': r':57[ACD]:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:)',  # Account With Institution
        'details_of_charges': r':71A:([A-Z]{3})',  # Details of Charges
    }
    
    # Transaction block patterns (multiple transactions)
    TRANSACTION_REF_PATTERN = r':21:([^\n:]+)'  # Transaction reference
    TRANSACTION_AMOUNT_PATTERN = r':32B:([A-Z]{3})([\d,\.]+)'  # Currency and amount
    BENEFICIARY_PATTERN = r':59:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:|$)'  # Beneficiary
    BENEFICIARY_BANK_PATTERN = r':57[ACD]:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:)'  # Beneficiary's bank
    REMITTANCE_INFO_PATTERN = r':70:((?:[^\n:]+\n?)+?)(?=:\d{2}[A-Z]?:|$)'  # Remittance information
    
    @staticmethod
    def parse(mt102_message: str) -> Dict:
        """
        Parse MT102 message into structured dictionary
        
        Args:
            mt102_message: Raw MT102 SWIFT message text
            
        Returns:
            Dictionary with parsed fields
            
        Raises:
            MT102MissingFieldError: If mandatory fields are missing
            MT102ValidationError: If field validation fails
        """
        parsed = {}
        
        # Extract mandatory fields
        mandatory_fields = [
            ('transaction_ref', ':20:'),
            ('ordering_customer', ':50'),
            ('value_date', ':32A:'),
            ('currency_amount', ':32A:'),
        ]
        
        for field_name, field_code in mandatory_fields:
            pattern = MT102Parser.FIELD_PATTERNS.get(field_name)
            if pattern:
                match = re.search(pattern, mt102_message, re.MULTILINE | re.DOTALL)
                if not match:
                    raise MT102MissingFieldError(
                        f"Mandatory field {field_code} not found in MT102 message"
                    )
                if field_name == 'currency_amount':
                    parsed['currency'] = match.group(1)
                    parsed['total_amount'] = match.group(2)
                else:
                    parsed[field_name] = match.group(1).strip()
        
        # Extract optional fields
        optional_fields = [
            'ordering_institution', 'account_with_institution', 'details_of_charges'
        ]
        
        for field_name in optional_fields:
            pattern = MT102Parser.FIELD_PATTERNS.get(field_name)
            if pattern:
                match = re.search(pattern, mt102_message, re.MULTILINE | re.DOTALL)
                if match:
                    parsed[field_name] = match.group(1).strip()
        
        # Parse multiple transactions
        parsed['transactions'] = MT102Parser._parse_transactions(mt102_message)
        
        return parsed
    
    @staticmethod
    def _parse_transactions(mt102_message: str) -> List[Dict]:
        """Parse individual transaction blocks from MT102"""
        transactions = []
        
        # Find all transaction references
        transaction_matches = list(re.finditer(MT102Parser.TRANSACTION_REF_PATTERN, mt102_message))
        
        for i, match in enumerate(transaction_matches):
            start_pos = match.start()
            end_pos = transaction_matches[i + 1].start() if i + 1 < len(transaction_matches) else len(mt102_message)
            transaction_block = mt102_message[start_pos:end_pos]
            
            transaction = MT102Parser._parse_single_transaction(transaction_block)
            if transaction:
                transaction['transaction_ref'] = match.group(1).strip()
                transactions.append(transaction)
        
        return transactions
    
    @staticmethod
    def _parse_single_transaction(transaction_block: str) -> Optional[Dict]:
        """Parse a single transaction from MT102"""
        transaction = {}
        
        # Amount and currency
        amount_match = re.search(MT102Parser.TRANSACTION_AMOUNT_PATTERN, transaction_block)
        if amount_match:
            transaction['currency'] = amount_match.group(1)
            amount_str = amount_match.group(2).replace(',', '')
            transaction['amount'] = Decimal(amount_str)
        
        # Beneficiary
        beneficiary_match = re.search(MT102Parser.BENEFICIARY_PATTERN, transaction_block, re.MULTILINE | re.DOTALL)
        if beneficiary_match:
            transaction['beneficiary'] = beneficiary_match.group(1).strip()
        
        # Beneficiary's bank
        bank_match = re.search(MT102Parser.BENEFICIARY_BANK_PATTERN, transaction_block, re.MULTILINE | re.DOTALL)
        if bank_match:
            transaction['beneficiary_bank'] = bank_match.group(1).strip()
        
        # Remittance information
        remit_match = re.search(MT102Parser.REMITTANCE_INFO_PATTERN, transaction_block, re.MULTILINE | re.DOTALL)
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


class Pacs008Mapper:
    """Maps parsed MT102 data to pacs.008 structure"""
    
    @staticmethod
    def map_to_pacs008(parsed_data: Dict) -> Pacs008Document:
        """
        Map parsed MT102 data to pacs.008 document structure
        
        Args:
            parsed_data: Dictionary from MT102Parser.parse()
            
        Returns:
            Pacs008Document instance
            
        Raises:
            Pacs008ConversionError: If mapping fails
        """
        try:
            # Parse ordering customer
            ordering_account, ordering_name, ordering_address = MT102Parser.parse_party_info(
                parsed_data.get('ordering_customer', '')
            )
            
            # Parse ordering institution (debtor agent)
            ordering_inst_text = parsed_data.get('ordering_institution', '')
            ordering_inst_bic = None
            ordering_inst_name = None
            if ordering_inst_text:
                ordering_inst_bic, ordering_inst_name, _ = MT102Parser.parse_party_info(ordering_inst_text)
            
            # Create group header
            num_transactions = len(parsed_data['transactions'])
            group_header = GroupHeader(
                MsgId=f"MSG{parsed_data['transaction_ref'][:30]}",
                CreDtTm=datetime.utcnow(),
                NbOfTxs=str(num_transactions),
                TtlIntrBkSttlmAmt=ActiveOrHistoricCurrencyAndAmount(
                    Ccy=parsed_data.get('currency', 'USD'),
                    value=Decimal(parsed_data.get('total_amount', '0').replace(',', ''))
                ),
                IntrBkSttlmDt=Pacs008Mapper._parse_value_date(parsed_data.get('value_date', '')),
                SttlmInf={'SttlmMtd': 'CLRG'},
                InstgAgt=BranchAndFinancialInstitutionIdentification(
                    FinInstnId=FinancialInstitutionIdentification(
                        BICFI=ordering_inst_bic if ordering_inst_bic and len(ordering_inst_bic) >= 8 else None,
                        Nm=ordering_inst_name
                    )
                ) if ordering_inst_bic or ordering_inst_name else None,
                InstdAgt=None
            )
            
            # Map charge bearer
            charge_bearer = Pacs008Mapper._map_charge_bearer(
                parsed_data.get('details_of_charges', 'SHA')
            )
            
            # Create credit transfer transactions
            credit_transfers = []
            for idx, txn in enumerate(parsed_data['transactions']):
                credit_transfer = Pacs008Mapper._create_credit_transfer(
                    txn, idx, parsed_data, ordering_account, ordering_name, 
                    ordering_address, ordering_inst_bic, ordering_inst_name, charge_bearer
                )
                credit_transfers.append(credit_transfer)
            
            # Create root document
            pacs008_doc = Pacs008Document(
                FIToFICstmrCdtTrf=FIToFICustomerCreditTransfer(
                    GrpHdr=group_header,
                    CdtTrfTxInf=credit_transfers
                )
            )
            
            return pacs008_doc
            
        except Exception as e:
            raise Pacs008ConversionError(f"Failed to map MT102 to pacs.008: {str(e)}")
    
    @staticmethod
    def _create_credit_transfer(
        txn: Dict,
        index: int,
        parsed_data: Dict,
        ordering_account: Optional[str],
        ordering_name: Optional[str],
        ordering_address: List[str],
        ordering_inst_bic: Optional[str],
        ordering_inst_name: Optional[str],
        charge_bearer: ChargeBearer
    ) -> CreditTransferTransaction:
        """Create a single credit transfer transaction"""
        
        # Parse beneficiary
        beneficiary_account, beneficiary_name, beneficiary_address = MT102Parser.parse_party_info(
            txn.get('beneficiary', '')
        )
        
        # Parse beneficiary's bank if present
        creditor_bic = None
        creditor_name = None
        if 'beneficiary_bank' in txn:
            bic, name, _ = MT102Parser.parse_party_info(txn['beneficiary_bank'])
            creditor_bic = bic
            creditor_name = name
        
        # Create payment identification
        payment_id = PaymentIdentification(
            InstrId=f"INSTR{index + 1:03d}",
            EndToEndId=txn.get('transaction_ref', f"E2E{index + 1:03d}"),
            TxId=f"TXN{index + 1:03d}"
        )
        
        # Create interbank settlement amount
        interbank_amount = ActiveOrHistoricCurrencyAndAmount(
            Ccy=txn.get('currency', parsed_data.get('currency', 'USD')),
            value=txn.get('amount', Decimal('0'))
        )
        
        # Create debtor (ordering customer)
        debtor = Party(
            Nm=ordering_name or "Unknown Debtor",
            PstlAdr=PostalAddress(
                AdrLine=ordering_address[:7] if ordering_address else None
            ) if ordering_address else None
        )
        
        # Create debtor account
        debtor_account = CashAccount(
            Id={"IBAN": ordering_account} if ordering_account and ordering_account.startswith(('GB', 'DE', 'FR', 'IT'))
                else {"Othr": {"Id": ordering_account or "UNKNOWN"}}
        )
        
        # Create debtor agent
        debtor_agent = BranchAndFinancialInstitutionIdentification(
            FinInstnId=FinancialInstitutionIdentification(
                BICFI=ordering_inst_bic if ordering_inst_bic and len(ordering_inst_bic) >= 8 else None,
                Nm=ordering_inst_name
            )
        ) if ordering_inst_bic or ordering_inst_name else None
        
        # Create creditor agent
        creditor_agent = BranchAndFinancialInstitutionIdentification(
            FinInstnId=FinancialInstitutionIdentification(
                BICFI=creditor_bic if creditor_bic and len(creditor_bic) >= 8 else None,
                Nm=creditor_name
            )
        ) if creditor_bic or creditor_name else None
        
        # Create creditor (beneficiary)
        creditor = Party(
            Nm=beneficiary_name or "Unknown Creditor",
            PstlAdr=PostalAddress(
                AdrLine=beneficiary_address[:7] if beneficiary_address else None
            ) if beneficiary_address else None
        )
        
        # Create creditor account
        creditor_account = CashAccount(
            Id={"IBAN": beneficiary_account} if beneficiary_account and beneficiary_account.startswith(('GB', 'DE', 'FR', 'IT'))
                else {"Othr": {"Id": beneficiary_account or "UNKNOWN"}}
        )
        
        # Create remittance information
        remittance_info = None
        if 'remittance_info' in txn:
            remittance_info = RemittanceInformation(
                Ustrd=[txn['remittance_info'][:140]]
            )
        
        return CreditTransferTransaction(
            PmtId=payment_id,
            IntrBkSttlmAmt=interbank_amount,
            ChrgBr=charge_bearer,
            Dbtr=debtor,
            DbtrAcct=debtor_account,
            DbtrAgt=debtor_agent,
            CdtrAgt=creditor_agent,
            Cdtr=creditor,
            CdtrAcct=creditor_account,
            RmtInf=remittance_info
        )
    
    @staticmethod
    def _map_charge_bearer(mt_charge_code: str) -> ChargeBearer:
        """Map MT102 charge code to pacs.008 charge bearer"""
        mapping = {
            'OUR': ChargeBearer.DEBT,
            'BEN': ChargeBearer.CRED,
            'SHA': ChargeBearer.SHAR,
        }
        return mapping.get(mt_charge_code.upper(), ChargeBearer.SHAR)
    
    @staticmethod
    def _parse_value_date(date_str: str) -> str:
        """Parse YYMMDD to ISO date format"""
        try:
            dt = datetime.strptime(date_str, '%y%m%d')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return datetime.utcnow().strftime('%Y-%m-%d')


class XMLGenerator:
    """Generates pacs.008 XML from Pydantic model"""
    
    @staticmethod
    def pacs008_to_xml(pacs008_doc: Pacs008Document) -> str:
        """
        Convert pacs.008 document to XML string
        
        Args:
            pacs008_doc: Pacs008Document instance
            
        Returns:
            Formatted XML string with namespaces
        """
        # Convert to dictionary
        doc_dict = pacs008_doc.model_dump(exclude_none=True, by_alias=False)
        
        # Wrap in Document root with namespaces
        xml_dict = {
            'Document': {
                '@xmlns': 'urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08',
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


def convert_mt102_to_pacs008(mt102_message: str) -> Tuple[str, str]:
    """
    Main conversion function: MT102 -> pacs.008 XML
    
    Args:
        mt102_message: Raw MT102 SWIFT message
        
    Returns:
        Tuple of (xml_output, input_hash)
        
    Raises:
        MT102ParseError: If parsing fails
        Pacs008ConversionError: If conversion fails
    """
    # Parse MT102
    parsed_data = MT102Parser.parse(mt102_message)
    
    # Map to pacs.008
    pacs008_doc = Pacs008Mapper.map_to_pacs008(parsed_data)
    
    # Generate XML
    xml_output = XMLGenerator.pacs008_to_xml(pacs008_doc)
    
    # Compute input hash for logging
    input_hash = hashlib.sha256(mt102_message.encode()).hexdigest()
    
    return xml_output, input_hash


def compute_input_hash(mt102_message: str) -> str:
    """Compute SHA256 hash of input for anonymized logging"""
    return hashlib.sha256(mt102_message.encode()).hexdigest()
