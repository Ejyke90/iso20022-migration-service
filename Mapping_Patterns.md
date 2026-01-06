# Mapping Strategy: Path-Driven Architecture

## 1. The "Path-to-Method" Rule
You must analyze the "Source Path" column to determine code structure. Do not map deep paths in the main strategy class.

**The Rule:**
1.  Identify the **Common Parent Path** for a group of fields.
2.  If the Parent Path represents a complex object (e.g., `.../InitgPty/`, `.../Dbtr/`, `.../FinInstnId/`), you **MUST** create a protected helper method.
3.  The Main Strategy class should only contain calls to these helper methods.

**Example:**
* **Input CSV Rows:**
    * `.../PmtInf/Dbtr/Nm`
    * `.../PmtInf/Dbtr/PstlAdr/StrtNm`
* **Analysis:** Both share `.../PmtInf/Dbtr/`.
* **Action:** Create `protected Debtor debtorMapping(Source.Dbtr input)`.
* **Main Class:** `@Mapping(target="debtor", expression="java(debtorMapping(source.getPmtInf().getDbtr()))")`

## 2. Null Safety & Path Traversal
The "Full Path" in the CSV corresponds to the `NullSafe` chain in Java.
* **CSV Path:** `A/B/C/Value`
* **Java Code:** `NullSafe.get(() -> source.getA().getB().getC().getValue())`

## 3. Variable naming
* Match the helper method name to the Target Path object name (e.g., Target `initiating_party` -> Method `initiatingPartyMapping`).
