# ISO20022 to Canonical Mapping Strategy: Path-Driven Architecture

## Project Overview
This document defines the exact coding standards, architectural patterns, and mapping strategies used in the Event Handler Service for transforming ISO20022 payment messages (Pain.001, Pain.008, Pacs.008, etc.) to a canonical business view format.

---

## 1. Core Architecture Pattern: Strategy + MapStruct

### 1.1 Strategy Class Structure
Each message type has a dedicated Strategy class that:
- Extends `CommonStrategy`
- Implements `BusinessViewMappingStrategy`
- Uses MapStruct for declarative mappings via `@Mapping` annotations
- Contains helper methods for complex nested object transformations

**Example:**
```java
@Mapper(imports = {UUID.class, Arrays.class, DateTime.class, DateTimeZone.class}, 
        builder = @Builder(disableBuilder = true), 
        nullValueCheckStrategy = NullValueCheckStrategy.ALWAYS)
@Slf4j
public abstract class Pain001Strategy extends CommonStrategy implements BusinessViewMappingStrategy {
    static Pain001Strategy MAPPER = Mappers.getMapper(Pain001Strategy.class);
    private static DatatypeFactory datatypeFactory;
    
    @Mappings({
        @Mapping(target = "businessView.podsblzview.paymentClassification", constant = SensConstants.EVENT_CLASSIFICATION),
        @Mapping(target = "businessView.podsblzview.channelId", constant = SensConstants.CHANNEL_ID),
        // ... more mappings
    })
    abstract Document pain001XMLtoAvroMapping(com.rbc.avro.xsd.pain001.Document document);
}
```

### 1.2 MapStruct Configuration
- **Builder disabled**: `@Builder(disableBuilder = true)`
- **Null value strategy**: `NullValueCheckStrategy.ALWAYS`
- **Static mapper instance**: `static MAPPER = Mappers.getMapper(StrategyClass.class)`

---

## 2. The "Path-to-Helper-Method" Rule

### 2.1 When to Create a Helper Method
Create a helper method when:
1. **Nested Complex Types**: A source path contains 3+ nested levels (e.g., `CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/IntrmyAgt1/FinInstId`)
2. **Repeating Structures**: The same complex type appears multiple times in the schema (e.g., `FinInstId` appears for multiple agents)
3. **List/Array Handling**: MapStruct struggles with nested lists - extract to helper method
4. **Type Conversion Required**: Custom logic needed (Date, Enum, Amount formatting)

### 2.2 Helper Method Naming Convention
**Pattern**: `{businessConceptName}Mapping`

**Examples:**
- `financialInstitutionIdentificationMapping()` - Maps FinInstId structure
- `cashAccount3BMapping()` - Maps account details
- `partyIdentification13SMapping()` - Maps party identification
- `postalAddress6Mapping()` - Maps postal address structure
- `instructionForCreditorAgentMapping()` - Maps instruction details

**Rule**: Name after the XSD complex type OR the business concept being mapped.

### 2.3 Helper Method Signature Pattern
```java
protected com.rbc.wk60.pods.paymentdomain.avro.podsblzview.FinancialInstitutionIdentification 
financialInstitutionIdentificationMapping(
    com.rbc.avro.xsd.pain001.BranchAndFinancialInstitutionIdentification branchAndFinancialInstitutionIdentification
) {
    // Implementation
}
```

**Key characteristics:**
- `protected` visibility (accessible to MapStruct)
- Returns canonical/target type
- Accepts source XSD type
- Full package names in signature for clarity

---

## 3. Null Safety Pattern: NullSafe.get()

### 3.1 The NullSafe Utility
**CRITICAL**: This project uses a custom `NullSafe.get()` utility, NOT Java's `Optional` or direct null checks.

**Syntax:**
```java
BigDecimal instructedAmt = NullSafe.get(() -> amount.getInstdAmt().getValue())
```

**What it does:**
- Wraps a lambda expression that navigates nested getters
- Returns `null` if any getter in the chain returns `null`
- Prevents `NullPointerException` without verbose null checks

### 3.2 Usage Rules
**Always use NullSafe.get() for:**
1. Navigating 2+ levels deep (e.g., `obj.getA().getB()`)
2. Accessing values from optional XSD elements
3. Before type conversions that don't accept null

**Example from code:**
```java
if (amount != null) {
    if (amount.getInstdAmt() != null) {
        BigDecimal instructedAmt = NullSafe.get(() -> amount.getInstdAmt().getValue());
        .setScale(BusinessViewConstants.SWIFT_FRACTION_DIGITS, RoundingMode.HALF_UP, new BigDecimal(val: 0));
        validateSwiftAmount(instructedAmt);
        amount.getInstdAmt().setValue(new BigDecimal(toSwiftCanonicalDecimal(instructedAmt)));
    }
}
```

### 3.3 When NOT to use NullSafe
- Direct null checks before method calls are acceptable for single-level access
- Example: `if (pmtInf == null) { return null; }`

---

## 4. Type Conversion Patterns

### 4.1 Standard Converters

#### **4.1.1 XML Date to Long (Unix Timestamp)**
```java
protected String retrieveUETR(com.rbc.avro.xsd.pain001.Document document) {
    if (document.getCstmrCdtTrfInitn() != null
        && document.getCstmrCdtTrfInitn().getPmtInf() != null
        && document.getCstmrCdtTrfInitn().getPmtInf().getCdtTrfTxInf() != null
        && document.getCstmrCdtTrfInitn().getPmtInf().getCdtTrfTxInf().getPmtId() != null
        && document.getCstmrCdtTrfInitn().getPmtInf().getCdtTrfTxInf().getPmtId().getUETR() != null) {
        return (document.getCstmrCdtTrfInitn().getPmtInf().getCdtTrfTxInf().getPmtId().getUETR());
    }
    return null;
}
```

**Pattern**: Chain null checks with `&&` for multi-level navigation.

#### **4.1.2 BigDecimal to Double**
```java
protected Double bigDecimalToDouble(BigDecimal input) {
    if (input != null) {
        return input.doubleValue();
    } else {
        return null;
    }
}
```

#### **4.1.3 String to Enum**
```java
protected com.rbc.wk60.pods.paymentdomain.avro.podsblzview.ChargeBearerTypeCode 
getPmtInfChargeBearer(com.rbc.avro.xsd.pain001.PaymentInstruction301 pmtInf) {
    return com.rbc.wk60.pods.paymentdomain.avro.podsblzview.ChargeBearerTypeCode.valueOf(
        pmtInf.getChrgBr().name()
    );
}
```

**Pattern**: Use `.valueOf()` for enum conversion with `.name()` from source enum.

### 4.2 Amount Validation and Formatting
**Swift Canonical Decimal Pattern:**
```java
BigDecimal instructedAmt = NullSafe.get(() -> amount.getInstdAmt().getValue())
    .setScale(BusinessViewConstants.SWIFT_FRACTION_DIGITS, RoundingMode.HALF_UP, new BigDecimal(0));
validateSwiftAmount(instructedAmt);
```

**Constants:**
- `BusinessViewConstants.SWIFT_FRACTION_DIGITS` - Decimal places for amounts
- `RoundingMode.HALF_UP` - Standard rounding mode

---

## 5. Mapping Annotation Patterns

### 5.1 Simple Field Mappings
```java
@Mapping(target = "paymentIdentification", 
         expression = "java(paymentIdentificationMapping(document.getCstmrCdtTrfInitn().getPmtInf()))")
```

**Pattern**: Use `expression = "java(...)"` for helper method calls.

### 5.2 Constant Mappings
```java
@Mapping(target = "businessView.podsblzview.paymentClassification", 
         constant = SensConstants.EVENT_CLASSIFICATION)
```

**Pattern**: Use `constant` for fixed values defined in constants classes.

### 5.3 Source Path Mappings
```java
@Mapping(source = "fwdgAgt.finInstnId.BICFI", 
         target = "financialInstitutionIdentification.bicfi")
```

**Pattern**: Use `source` for direct path mappings when no transformation needed.

### 5.4 Retrieving from Document
```java
@Mapping(target = "uetr", 
         expression = "java(retrieveUETR(document))")
```

**Pattern**: For deeply nested fields, create a `retrieve{FieldName}` method.

---

## 6. CSV-to-Code Mapping Strategy

### 6.1 CSV Structure
**Format:**
```
Source Path,Target Canonical
CstmrCdtTrfInitn/PmtInf/PmtInfId,payment_identification.payment_information_identification
CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/PmtId/InstrId,payment_identification.instruction_identification
```

### 6.2 Path Analysis Algorithm
**Step 1: Group by Parent Path**
- Extract common parent (e.g., `CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/IntrmyAgt1/FinInstId`)
- All children of this parent go into ONE helper method

**Step 2: Determine Helper Method Name**
- Use the final complex type name: `FinInstId` → `financialInstitutionIdentificationMapping`
- Or use business concept: `PstlAdr` → `postalAddress6Mapping`

**Step 3: Generate @Mapping Annotations**
- Top-level fields → Direct `@Mapping` with `expression = "java(helperMethod())"`
- Nested repeated structures → Helper method with internal mappings

### 6.3 Example Transformation

**CSV Input:**
```
CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/IntrmyAgt1/FinInstId/BICFI,intermediary_agent_1.financial_institution_identification.bicfi
CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/IntrmyAgt1/FinInstId/ClrSysMmbId/ClrSysId,intermediary_agent_1.financial_institution_identification.clearing_system_member_identification.clearing_system_identification.code
```

**Generated Code:**
```java
@Mapping(target = "intermediaryAgent1", 
         expression = "java(financialInstitutionIdentificationMapping(document.getCstmrCdtTrfInitn().getPmtInf().getCdtTrfTxInf().getIntrmyAgt1()))")

protected FinancialInstitutionIdentification financialInstitutionIdentificationMapping(
    BranchAndFinancialInstitutionIdentification intrmyAgt) {
    if (intrmyAgt == null || intrmyAgt.getFinInstId() == null) {
        return null;
    }
    
    FinancialInstitutionIdentification result = FinancialInstitutionIdentification.newBuilder()
        .setBicfi(NullSafe.get(() -> intrmyAgt.getFinInstId().getBICFI()))
        .setClearingSystemMemberIdentification(
            clearingSystemMemberIdentificationMapping(intrmyAgt.getFinInstId().getClrSysMmbId())
        )
        .build();
    
    return result;
}
```

---

## 7. Error Handling Pattern

### 7.1 Try-Catch in Entry Point
```java
protected AmountType4Choice mapValidatedAmount(com.rbc.avro.xsd.pain001.Document document) {
    try {
        com.rbc.avro.xsd.pain001.AmountType4Choice amount = 
            document.getCstmrCdtTrfInitn().getPmtInf().getCdtTrfTxInf().getAmt();
        if (amount == null) {
            log.error("Error while mapping Instructed Amount : Amount is null");
            return null;
        }
        // Validation logic...
        return amount;
    } catch (MappingException ex) {
        log.error("Error while mapping Instructed Amount: {}", ex.getMessage());
        return null;
    }
}
```

**Pattern:**
- Catch `MappingException` at validation/transformation entry points
- Log error with context
- Return `null` (MapStruct will handle nulls)

### 7.2 Null Guard Pattern
```java
if (pmtInf == null) {
    return null;
}
```

**Rule**: Always check the main parameter for null at the start of helper methods.

---

## 8. Schema Namespace Handling

### 8.1 Forced Namespace Replacement
```java
public static String forceNamespaceChange(String documentXmlPayload, String pain001ForcedNamespace) {
    // Regex matches "xsd:pain\\.001\\.001\\.\\d{2}" followed by any two characters
    String pattern = "(xsd:pain\\.001\\.001\\.\\d{2})(\\w{2})";
    
    // Replace with "xsd:pain.001.001.09"
    String replacement = "$1" + "09";
    
    // Apply replacement only to Document section
    if (documentXmlPayload.contains(str: "<Document")) {
        int docStart = documentXmlPayload.indexOf(str: "<Document");
        int docEnd = documentXmlPayload.indexOf(str: "</Document>") + "</Document>".length();
        
        String beforeDoc = documentXmlPayload.substring(beginIndex: 0, docStart);
        String docSection = documentXmlPayload.substring(docStart, docEnd);
        String afterDoc = documentXmlPayload.substring(docEnd);
        
        // Apply replacement
        String modifiedDocSection = docSection.replaceAll(pattern, replacement);
        
        return beforeDoc + modifiedDocSection + afterDoc;
    }
    return documentXmlPayload;
}
```

**Purpose**: Handle XSD version mismatches by forcing namespace to expected version.

---

## 9. Code Generation Rules Summary

### 9.1 From CSV Mapping Matrix
**Input**: CSV with Source Path, Target Canonical

**Output Generation Steps:**
1. **Parse CSV**: Extract all source-target pairs
2. **Group by Parent**: Identify common parent paths (3+ levels deep)
3. **Create Helper Methods**: One per repeated complex type
4. **Generate @Mappings**: Top-level fields use `expression = "java(helper())"`
5. **Apply Null Safety**: Wrap nested getters with `NullSafe.get()`
6. **Add Type Converters**: Detect data type mismatches (Date, Amount, Enum)
7. **Insert Null Guards**: Start each helper with `if (param == null) return null;`

### 9.2 Verification Checklist
- [ ] All CSV rows mapped to either `@Mapping` or helper method
- [ ] Helper methods use NullSafe.get() for nested navigation
- [ ] Type converters applied where needed
- [ ] Null guards at method entry
- [ ] MapStruct annotations correct (`target`, `source`, `expression`)
- [ ] Constants used from SensConstants/BusinessViewConstants

---

## 10. Integration with Event Handler Service

### 10.1 Strategy Invocation Pattern
```java
// In event consumer
Document transformedDocument = Pain001Strategy.MAPPER.pain001XMLtoAvroMapping(sourceDocument);
```

**Key Points:**
- Use static MAPPER instance
- One method call performs entire transformation
- MapStruct + helper methods execute automatically

### 10.2 Validation Integration
```java
protected AmountType4Choice mapValidatedAmount(Document document) {
    // Retrieve amount
    // Validate with validateSwiftAmount()
    // Format with toSwiftCanonicalDecimal()
    // Return validated amount
}
```

**Pattern**: Validation happens INSIDE helper methods, not in consumer.

---

## 11. Reusable Components

### 11.1 Common Helper Methods (Across All Message Types)
- `financialInstitutionIdentificationMapping()` - Used by Pain.001, Pacs.008, etc.
- `postalAddressMapping()` - Address structures
- `cashAccountMapping()` - Account details
- `partyIdentificationMapping()` - Party info

### 11.2 When to Reuse vs. Create New
**Reuse if:**
- XSD complex type has SAME structure across message types
- Field names and nesting identical

**Create new if:**
- Field names differ (e.g., `Cdtr` vs `Dbtr`)
- Additional validation rules specific to message type

---

## 12. Future AI Agent Instructions

### 12.1 To Generate Code from CSV + Schemas:
1. Load source XSD schema
2. Load target Avro/XSD schema
3. Parse mapping CSV
4. For each unique parent path:
   - Check if it's a complex type (3+ fields)
   - If yes: Create helper method
   - If no: Use direct `@Mapping`
5. Generate helper method signature from XSD types
6. Generate helper method body:
   - Null guard
   - Builder pattern for target object
   - NullSafe.get() for nested access
   - Call child helper methods for nested complex types
7. Generate `@Mappings` block with all top-level mappings
8. Add type converters where source/target types differ

### 12.2 Validation Rules:
- Every source path in CSV must appear in generated code
- Every complex type with 3+ children gets a helper method
- No direct null checks without `NullSafe.get()`
- All amounts validated with SWIFT decimal rules

---

## End of Document
**Version**: 1.0  
**Last Updated**: Generated from Pain001Strategy.java analysis  
**Applies To**: All ISO20022 message type transformations in Event Handler Service
