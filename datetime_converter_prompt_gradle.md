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
- **Build Tool**: Gradle (Kotlin DSL preferred, Groovy DSL acceptable)
- **Dependencies**: 
  - Use only `java.time` API (no external datetime libraries like Joda-Time)
  - JUnit 5 (Jupiter) for testing
  - Gradle plugins for packaging and deployment
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
├── build.gradle.kts (or build.gradle for Groovy DSL)
├── settings.gradle.kts (or settings.gradle)
├── gradle.properties
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

### Gradle Configuration

#### build.gradle.kts (Kotlin DSL - RECOMMENDED)

Required configuration elements:

1. **Plugins**:
   - `java-library` (for library publishing)
   - `maven-publish` (for publishing artifacts)
   - `signing` (for signing artifacts - Maven Central requirement)
   - `jacoco` (for code coverage reports)

2. **Project Metadata**:
   - **Group**: `com.datetimeutils`
   - **Artifact ID**: `datetime-converter`
   - **Version**: `1.0.0`

3. **Java Configuration**:
   - Source compatibility: Java 11
   - Target compatibility: Java 11
   - Enable Java toolchain (optional but recommended)

4. **Dependencies**:
   - JUnit 5 (Jupiter) for testing: `testImplementation("org.junit.jupiter:junit-jupiter:5.9.3")`
   - Configure test task to use JUnit Platform

5. **Publishing Configuration**:
   - Configure `maven-publish` plugin with:
     - Publication name: `mavenJava`
     - From components: `components["java"]`
     - Generate sources JAR
     - Generate JavaDoc JAR
     - POM configuration (name, description, URL, licenses, developers, SCM)
   - Configure repository:
     - OSSRH snapshot repository: `https://s01.oss.sonatype.org/content/repositories/snapshots/`
     - OSSRH release repository: `https://s01.oss.sonatype.org/service/local/staging/deploy/maven2/`
     - Credentials from `gradle.properties` or environment variables

6. **Signing Configuration**:
   - Sign all publications
   - Configure GPG key from `gradle.properties` or environment variables

7. **Tasks**:
   - Custom task for generating sources JAR
   - Custom task for generating JavaDoc JAR
   - Configure JavaDoc options (links to Java SE docs)

#### settings.gradle.kts
```kotlin
rootProject.name = "datetime-converter"
```

#### gradle.properties
Include template with:
```properties
# Project properties
version=1.0.0
group=com.datetimeutils

# Sonatype credentials (DO NOT commit these - use local gradle.properties or env vars)
# ossrhUsername=your-username
# ossrhPassword=your-password

# Signing configuration (DO NOT commit these)
# signing.keyId=your-key-id
# signing.password=your-password
# signing.secretKeyRingFile=/path/to/secring.gpg
```

### Documentation Requirements

#### README.md Must Include:
1. **Project Description**: Clear explanation of what the library does
2. **Features**: List of key features
3. **Installation Instructions**:
   - Gradle (Kotlin DSL) dependency snippet:
     ```kotlin
     dependencies {
         implementation("com.datetimeutils:datetime-converter:1.0.0")
     }
     ```
   - Gradle (Groovy DSL) dependency snippet:
     ```groovy
     dependencies {
         implementation 'com.datetimeutils:datetime-converter:1.0.0'
     }
     ```
   - Maven dependency snippet (for Maven users):
     ```xml
     <dependency>
         <groupId>com.datetimeutils</groupId>
         <artifactId>datetime-converter</artifactId>
         <version>1.0.0</version>
     </dependency>
     ```
4. **Quick Start Guide**: Simple code examples
5. **Usage Examples**: 
   - Converting Instant to EST (primary use case)
   - Converting EST back to Instant
   - Working with Instant objects from databases/APIs
   - Converting between timezones
   - Using OffsetDateTime for fixed offsets
6. **Supported Timezones**: Table with timezone IDs and descriptions
7. **API Documentation**: Link to JavaDoc
8. **Building from Source**: Instructions to clone and build with Gradle
9. **Contributing Guidelines**: How to add new timezones
9. **Contributing Guidelines**: How to add new timezones
10. **License Information**: Apache License 2.0 or MIT

#### JavaDoc Requirements:
- Class-level documentation for all public classes
- Method-level documentation with `@param`, `@return`, `@throws`
- Usage examples in JavaDoc using `@example` or code blocks
- Package-level documentation (`package-info.java`)

### Packaging and Distribution

#### Step 1: Local Building and Testing
Create instructions for:
- Building the JAR: `./gradlew build`
- Running tests: `./gradlew test`
- Generating code coverage report: `./gradlew jacocoTestReport`
- Installing to local Maven repository: `./gradlew publishToMavenLocal`
- Generating JavaDoc: `./gradlew javadoc`
- Viewing JavaDoc: Location in `build/docs/javadoc/index.html`

#### Step 2: Maven Central Publication
Provide complete guide for publishing to Maven Central using Gradle:

1. **Prerequisites**:
   - Create Sonatype JIRA account at https://issues.sonatype.org
   - Request access for your group ID (`com.datetimeutils`)
   - Generate GPG key for signing artifacts:
     ```bash
     gpg --gen-key
     gpg --list-keys
     gpg --keyserver keyserver.ubuntu.com --send-keys YOUR_KEY_ID
     ```
   - Configure `~/.gradle/gradle.properties` with credentials (keep secure, don't commit):
     ```properties
     ossrhUsername=your-jira-username
     ossrhPassword=your-jira-password
     signing.keyId=last-8-digits-of-your-gpg-key
     signing.password=your-gpg-passphrase
     signing.secretKeyRingFile=/path/to/.gnupg/secring.gpg
     ```

2. **Build Configuration Requirements**:
   - Project POM metadata in `build.gradle.kts`:
     - name: Human-readable project name
     - description: Clear description of library purpose
     - url: GitHub repository URL
     - licenses: Apache License 2.0 or MIT
     - developers: Developer name and email
     - scm: GitHub repository connection info (connection, developerConnection, url)

3. **Publishing Commands**:
   - Build and publish to staging: `./gradlew publish`
   - Or use combined command: `./gradlew publishToSonatype closeAndReleaseSonatypeStagingRepository`
   - Manual release via Sonatype OSSRH UI at https://s01.oss.sonatype.org/

4. **Release Process**:
   - Run `./gradlew publish` to upload to staging repository
   - Log into https://s01.oss.sonatype.org/
   - Navigate to "Staging Repositories"
   - Find your repository, click "Close"
   - After validation passes, click "Release"
   - Artifacts will sync to Maven Central within 30 minutes to 2 hours

5. **Alternative: Automated Release**:
   - Add `io.github.gradle-nexus.publish-plugin` plugin
   - Configure for automatic close and release
   - Command: `./gradlew publishToSonatype closeAndReleaseSonatypeStagingRepository`

#### Step 3: Alternative Distribution Options

**Option A: GitHub Packages**
- Configuration for GitHub Packages repository in `build.gradle.kts`
- Authentication using GitHub token
- Publishing command: `./gradlew publish`
- Usage requires users to add GitHub Packages repository

**Option B: JitPack** (Easiest for open source)
- No configuration needed in build file
- Simply tag a release on GitHub
- Users can depend on: `implementation("com.github.yourusername:datetime-converter:1.0.0")`
- Add JitPack repository: `maven("https://jitpack.io")`

#### Step 4: GitHub Repository Setup
- Initialize Git repository: `git init`
- Create `.gitignore` for Java/Gradle projects:
  ```
  .gradle/
  build/
  .idea/
  *.iml
  out/
  gradle.properties  # If contains sensitive data
  ```
- Add comprehensive README.md
- Include LICENSE file (Apache 2.0 or MIT)
- Create initial commit and push to GitHub
- Create releases/tags for versions
- Set up GitHub Actions for CI/CD (optional but recommended):
  - Workflow for running tests on PRs
  - Workflow for building and validating releases
  - Optional: Automated publishing workflow

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
- [ ] Complete `build.gradle.kts` (Kotlin DSL preferred) with all required plugins and configuration
- [ ] `settings.gradle.kts` file
- [ ] `gradle.properties` template with placeholder values
- [ ] Detailed `README.md` with installation and usage instructions
- [ ] `LICENSE` file (Apache 2.0 or MIT)
- [ ] `.gitignore` file for Java/Gradle projects
- [ ] Step-by-step guide for publishing to Maven Central using Gradle
- [ ] JavaDoc comments on all public APIs
- [ ] Example code snippets showing Gradle dependency usage
- [ ] Instructions for local installation and testing using Gradle commands
- [ ] Guide for contributing/extending timezones
- [ ] CI/CD configuration (GitHub Actions workflow) - optional
- [ ] Alternative build file in Groovy DSL (`build.gradle`) - optional

### Success Criteria

The implementation is complete when:
1. All unit tests pass with >80% coverage (verify with `./gradlew jacocoTestReport`)
2. JAR can be built successfully with `./gradlew build`
3. Library can be installed locally with `./gradlew publishToMavenLocal` and used in another project
4. README provides clear instructions for all use cases
5. All public APIs have comprehensive JavaDoc
6. Code follows Java best practices and conventions
7. Publishing instructions for Maven Central using Gradle are clear and actionable
8. Build is reproducible and doesn't depend on IDE-specific configurations

## Additional Instructions for AI

- Use modern Java idioms and best practices
- Prioritize code readability and maintainability
- Include error messages that help developers debug issues
- Make the API intuitive and self-documenting
- Provide both simple convenience methods and flexible generic methods
- Consider future extensibility in the design
- Include performance considerations in JavaDoc where relevant

Please implement this complete library with all required files, documentation, and deployment instructions.
