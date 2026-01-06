<reverse_engineering_task>
    <role>Senior Software Architect & Pattern Extraction Agent</role>
    <objective>
        Analyze the current codebase to extract the "Integration DNA" of the project. 
        Your goal is to generate a set of reusable instruction files that will allow another AI to replicate this exact architecture for a new message type.
    </objective>

    <scope_of_analysis>
        You must review the following file types deeply:
        1. **Transformation Logic:** 'Pain001Strategy.java' (and similar Strategy classes).
           - Look for: How are helper methods structured? How is 'NullSafe' used? How are complex types handled?
        2. **Schemas:** The Source XSD and Target Avro/AVSC files.
           - Look for: Naming conventions (Snake_case vs CamelCase), namespace handling.
        3. **Mapping Definitions:** The 'Mapping_Matrix.csv' (or equivalent).
           - Look for: The relationship between the "Source Path" column and the Java code hierarchy.
    </scope_of_analysis>

    <extraction_rules>
        **1. Identify the Hierarchy Pattern:**
        - Analyze how deep paths (e.g., 'A/B/C/D') are broken down. 
        - Determine the "Grouping Rule": At what path depth does the code switch from a main method to a helper method? (e.g., "Any complex object path triggers a protected helper method").

        **2. Identify the Safety Pattern:**
        - Extract the exact syntax used for null checks. (e.g., "NullSafe.get(() -> ...)" vs "Optional.ofNullable").

        **3. Identify the Type Pattern:**
        - Find the utility methods used for specific type pairs (XMLGregorianCalendar -> Long, String -> Enum).
    </extraction_rules>

    <required_output>
        Based on your analysis, generate exactly TWO files in Markdown code blocks:

        **Output 1: 'MAPPING_PATTERNS.md'**
        - A human-readable guide describing the patterns you found.
        - Must include a "Path-to-Method" rule section.
        - Must include a table of "Standard Type Converters" found in the code.
        - Must include the specific "Null Safety" syntax rule.

        **Output 2: 'GENERATOR_PROMPT.xml'**
        - A prompt template that I can use for the *next* project.
        - It should accept a new CSV and new XSD/Avro as inputs.
        - It must explicitly instruct the future AI to follow the hierarchy and safety rules you just discovered.
    </required_output>
</reverse_engineering_task>
