# Comprehensive Prompt: Java DateTime Utility Converter Library

## Project Overview
Create a complete, production-ready Java library called **datetime-converter** that converts timestamps between UTC and various timezones. The library must be packaged and publishable for use by anyone online.

**Design Philosophy**: The library uses an **Instant-first approach** where `Instant` (representing a point in time in UTC) is the primary data type for conversions. This aligns with modern Java best practices and ensures unambiguous timestamp handling. `ZonedDateTime` is used as the output format for display purposes and as a convenience input option.

## Requirements

### Core Functionality
1. **Instant to Timezone Conversion**: Convert UTC instant to any supported timezone (returns ZonedDateTime)
2. **Timezone to Instant Conversion**: Convert from any supported timezone back to UTC instant
3. **Between Timezone Conversion**: Convert ZonedDateTime from one timezone to another (convenience method)
4. **Fixed Offset Support**: Convert Instant to OffsetDateTime with fixed UTC offset
5. **Initial Timezone Support**: Must support at least 5 timezones:
   - EST/EDT (America/New_York) - REQUIRED as first timezone
   - PST/PDT (America/Los_Angeles)
   - GMT/BST (Europe/London)
   - JST (Asia/Tokyo)
   - AEST/AEDT (Australia/Sydney)
4. **Extensibility**: Design must allow easy addition of more timezones
5. **DST Handling**: Automatically handle Daylight Saving Time transitions
6. **Thread Safety**: All operations must be thread-safe

### Technical Specifications

#### Technology Stack
- **Java Version**: Java 11 or higher
- **Build Tool**: Maven
- **Dependencies**: 
  - Use only `java.time` API (no external datetime libraries like Joda-Time)
  - JUnit 5 for testing
  - Maven plugins for packaging and deployment
- **Code Quality**: Include comprehensive JavaDoc comments

#### Project Structure
```
datetime-converter/
├── src/
│   ├── main/
│   │   └── java/
│   │       └── com/datetimeutils/converter/
│   │           ├── DateTimeConverter.java (main API class)
│   │           ├── TimeZoneRegistry.java (timezone management)
│   │           ├── ConversionResult.java (wrapper for results)
│   │           └── exception/
│   │               └── DateTimeConversionException.java
│   └── test/
│       └── java/
│           └── com/datetimeutils/converter/
│               ├── DateTimeConverterTest.java
│               └── TimeZoneRegistryTest.java
├── pom.xml
├── README.md
├── LICENSE
└── .gitignore
```

### Implementation Requirements

#### 1. DateTimeConverter Class
Create the main utility class with the following methods:

**Primary API - Instant-based (RECOMMENDED):**
- `ZonedDateTime toTimeZone(Instant instant, ZoneId targetZone)` - Convert UTC instant to any timezone
- `ZonedDateTime toTimeZone(Instant instant, String targetZoneId)` - String overload
- `Instant toUTC(ZonedDateTime zonedDateTime)` - Convert any timezone to UTC instant
- `OffsetDateTime toOffset(Instant instant, ZoneOffset offset)` - Convert to fixed offset

**Convenience Methods for Each Supported Timezone (Instant-based):**
- `ZonedDateTime toEST(Instant instant)` - Convert instant to EST
- `Instant fromEST(ZonedDateTime estDateTime)` - Convert EST to instant
- Similar methods for PST, GMT, JST, AEST

**Secondary API - ZonedDateTime overloads (for convenience):**
- `ZonedDateTime convertBetweenZones(ZonedDateTime source, ZoneId targetZone)` - Convert between timezones
- `ZonedDateTime convertBetweenZones(ZonedDateTime source, String targetZoneId)` - String overload

**Validation Methods:**
- `boolean isValidTimeZone(String zoneId)`
- `List<String> getSupportedTimeZones()`

#### 2. TimeZoneRegistry Class
- Maintain a registry of supported timezone IDs
- Provide methods to add/remove timezones dynamically
- Include timezone metadata (display name, offset)

#### 3. ConversionResult Class
A wrapper class that includes:
- The converted `ZonedDateTime`
- The source `Instant`
- Source timezone (if applicable)
- Target timezone
- Conversion timestamp (Instant)

#### 4. Exception Handling
Create custom exception `DateTimeConversionException` for:
- Invalid timezone IDs
- Null input validation
- Unsupported timezone conversions

#### 5. Unit Tests
Comprehensive test coverage including:
- Valid conversions from Instant to all supported timezones
- UTC round-trip conversions (Instant → ZonedDateTime → Instant)
- Between-timezone conversions (EST → PST, etc.)
- DST transition handling (test specific dates that cross DST boundaries)
- Edge cases (leap years, end of month, epoch time, far future dates)
- Invalid input handling (null Instant, invalid zone IDs)
- Thread safety tests with concurrent conversions
- OffsetDateTime conversion accuracy
- Verify Instant remains unchanged in round-trip conversions

### Maven Configuration (pom.xml)

#### Required Elements:
1. **Group ID**: `com.datetimeutils`
2. **Artifact ID**: `datetime-converter`
3. **Version**: `1.0.0`
4. **Packaging**: `jar`
5. **Java Version**: 11
6. **Dependencies**: JUnit 5 for testing
7. **Plugins**:
   - `maven-compiler-plugin` (Java 11)
   - `maven-source-plugin` (generate sources JAR)
   - `maven-javadoc-plugin` (generate JavaDoc JAR)
   - `maven-gpg-plugin` (for signing - Maven Central requirement)
   - `nexus-staging-maven-plugin` (for Maven Central deployment)

#### Distribution Management:
Configure for OSSRH (Sonatype) repository for Maven Central publication

### Documentation Requirements

#### README.md Must Include:
1. **Project Description**: Clear explanation of what the library does
2. **Features**: List of key features
3. **Installation Instructions**:
   - Maven dependency snippet
   - Gradle dependency snippet
4. **Quick Start Guide**: Simple code examples
5. **Usage Examples**: 
   - Converting Instant to EST (primary use case)
   - Converting EST back to Instant
   - Working with Instant objects from databases/APIs
   - Converting between timezones
   - Using OffsetDateTime for fixed offsets
6. **Supported Timezones**: Table with timezone IDs and descriptions
7. **API Documentation**: Link to JavaDoc
8. **Building from Source**: Instructions to clone and build
9. **Contributing Guidelines**: How to add new timezones
10. **License Information**: Apache License 2.0 or MIT

#### JavaDoc Requirements:
- Class-level documentation for all public classes
- Method-level documentation with `@param`, `@return`, `@throws`
- Usage examples in JavaDoc using `@example` or code blocks
- Package-level documentation (`package-info.java`)

### Packaging and Distribution

#### Step 1: Local Packaging
Create instructions for:
- Building the JAR: `mvn clean package`
- Installing locally: `mvn clean install`
- Generating JavaDoc: `mvn javadoc:javadoc`

#### Step 2: Maven Central Publication
Provide complete guide for publishing to Maven Central:

1. **Prerequisites**:
   - Create Sonatype JIRA account
   - Generate GPG key for signing artifacts
   - Configure `~/.m2/settings.xml` with credentials

2. **POM Requirements**:
   - Project name, description, URL
   - License information
   - Developer information
   - SCM information (GitHub repository)

3. **Deployment Commands**:
   - `mvn clean deploy` (to staging)
   - Release process via Sonatype OSSRH

4. **Alternative Distribution**: GitHub Packages
   - Configuration for GitHub Packages repository
   - Authentication setup
   - Publishing workflow

#### Step 3: GitHub Repository Setup
- Initialize Git repository
- Create `.gitignore` for Java/Maven projects
- Add comprehensive README.md
- Include LICENSE file (Apache 2.0 or MIT)
- Set up GitHub Actions for CI/CD (optional but recommended)

### Quality Requirements

#### Code Quality:
- Follow Java naming conventions
- Use meaningful variable and method names
- Keep methods focused and under 30 lines where possible
- Use Java 11+ features (var keyword, enhanced switch, etc.)
- No compiler warnings

#### Testing:
- Minimum 80% code coverage
- Test both happy paths and error cases
- Include parameterized tests for multiple timezones
- Performance tests for concurrent usage

#### Security:
- Input validation on all public methods
- No exposure of internal state
- Immutable objects where appropriate

### Example Usage Code

Include these examples in README:

```java
// Example 1: Convert UTC Instant to EST (RECOMMENDED APPROACH)
DateTimeConverter converter = new DateTimeConverter();
Instant now = Instant.now();
ZonedDateTime estTime = converter.toEST(now);
System.out.println("EST Time: " + estTime);

// Example 2: Convert EST back to UTC Instant
Instant utcInstant = converter.toUTC(estTime);
System.out.println("UTC Instant: " + utcInstant);

// Example 3: Generic timezone conversion from Instant
Instant instant = Instant.now();
ZonedDateTime jstTime = converter.toTimeZone(instant, ZoneId.of("Asia/Tokyo"));
System.out.println("JST Time: " + jstTime);

// Example 4: Convert between timezones (when you already have ZonedDateTime)
ZonedDateTime estDateTime = ZonedDateTime.now(ZoneId.of("America/New_York"));
ZonedDateTime pstTime = converter.convertBetweenZones(estDateTime, ZoneId.of("America/Los_Angeles"));
System.out.println("PST Time: " + pstTime);

// Example 5: Working with fixed offsets
Instant timestamp = Instant.now();
OffsetDateTime offsetTime = converter.toOffset(timestamp, ZoneOffset.ofHours(-5));
System.out.println("UTC-5 Time: " + offsetTime);

// Example 6: Parse timestamp from database and convert to user's timezone
long epochMillis = 1704067200000L; // from database
Instant dbInstant = Instant.ofEpochMilli(epochMillis);
ZonedDateTime userTime = converter.toTimeZone(dbInstant, "Australia/Sydney");
```

### Deliverables Checklist

Ensure the AI provides:
- [ ] Complete source code for all classes
- [ ] Comprehensive unit tests (JUnit 5)
- [ ] Complete `pom.xml` with all required plugins and configuration
- [ ] Detailed `README.md` with installation and usage instructions
- [ ] `LICENSE` file
- [ ] `.gitignore` file for Java/Maven
- [ ] Step-by-step guide for publishing to Maven Central
- [ ] JavaDoc comments on all public APIs
- [ ] Example code snippets
- [ ] Instructions for local installation and testing
- [ ] Guide for contributing/extending timezones
- [ ] CI/CD configuration (GitHub Actions workflow) - optional

### Success Criteria

The implementation is complete when:
1. All unit tests pass with >80% coverage
2. JAR can be built successfully with `mvn clean package`
3. Library can be installed locally and used in another project
4. README provides clear instructions for all use cases
5. All public APIs have comprehensive JavaDoc
6. Code follows Java best practices and conventions
7. Publishing instructions are clear and actionable

## Additional Instructions for AI

- Use modern Java idioms and best practices
- Prioritize code readability and maintainability
- Include error messages that help developers debug issues
- Make the API intuitive and self-documenting
- Provide both simple convenience methods and flexible generic methods
- Consider future extensibility in the design
- Include performance considerations in JavaDoc where relevant

Please implement this complete library with all required files, documentation, and deployment instructions.
