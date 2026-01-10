@Codebase Act as a Principal AI Architect. I want to install the "Working Group + Gatekeeper" AI architecture in this repository, but customized for this specific technology stack.

Task: Analyze the current codebase (look at package.json, pom.xml, requirements.txt, or file extensions) to determine the tech stack.

Then, generate a bash script named setup_custom_agents.sh that creates the following 5 files in .ai/capabilities/. You must rewrite the "Standards" section of each file to match the detected technology.

The Agents to Create:

architect.md: Enforce best practices for this language (e.g., if Node, enforce Async/Await; if Python, enforce PEP8).

security.md: Enforce OWASP standards specific to this framework (e.g., if React, check XSS; if SQL, check Injection).

performance.md: Identify specific bottlenecks for this runtime (e.g., React render cycles, Java Garbage Collection, Node Event Loop blocks).

sdet.md: Enforce the standard testing library for this stack (e.g., Jest, PyTest, JUnit) and assertions.

z_release_mgr.md: Enforce Conventional Commits (this is language agnostic).

Output: Provide only the complete setup_custom_agents.sh script in a single code block. Ensure the script also generates the strict .windsurfrules Prime Directive we discussed.