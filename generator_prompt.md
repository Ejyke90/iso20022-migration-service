<context_engineering_task>
    <role>Senior Integration Engineer</role>
    <goal>Generate a MapStruct Strategy class using Path-Based Decomposition.</goal>
    
    <inputs>
        <input_1>MAPPING_PATTERNS.md</input_1>
        <input_2>Mapping_Matrix.csv (Columns: SourceFullXPath, TargetCanonicalPath)</input_2>
    </inputs>

    <step_1_path_analysis>
        Before generating code, group the CSV rows by their **Target Parent Path**.
        
        Example grouping:
        - Group 'InitiatingParty': All rows mapping to 'target.payment_identification.initiating_party.*'
        - Group 'Debtor': All rows mapping to 'target.payment_identification.debtor.*'
        
        For each group, define:
        1. The Source Parent Path (e.g., '.../GrpHdr/InitgPty')
        2. The Method Name (e.g., 'initiatingPartyMapping')
    </step_1_path_analysis>

    <step_2_code_generation>
        Generate the Java Class 'Pain001Strategy'.
        
        **Rule 1 (The Root):** In the main @Mappings, only map the High-Level Groups identified in Step 1.
        
        **Rule 2 (The Helpers):** Generate a protected method for each Group.
           - Inside the helper, map the *relative* path (the "Leaf" nodes).
           - Example: If Source Path is '.../FinInstnId/BICFI', inside the helper 'financialInstitutionMapping', the source is just 'BICFI'.
        
        **Rule 3 (Type Conversion):** Check the specific field types. If the CSV implies a transformation (Date/Amount), wrap the mapping in the utility expressions defined in 'MAPPING_PATTERNS.md'.
    </step_2_code_generation>
</context_engineering_task>
