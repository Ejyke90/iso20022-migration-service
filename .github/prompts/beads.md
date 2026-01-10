I want to transform this repository into an "AI-Enabled" repo following the "Vibe Coding" methodology by Steve Yegge. We will use the "Beads" framework to give you persistent memory.

Please perform the following steps:

1.  **Install the Tool**
    * Check if `brew` is available. If so, run: `brew install steveyegge/beads/bd`
    * If not, try npm: `npm install -g @beads/bd`
    * Verify installation with `bd --version`

2.  **Initialize Memory**
    * Run `bd init` in the root of the workspace. This will create a hidden `.beads/` directory where you will store your memory (issues/tasks) as JSONL files.

3.  **Create "Fire Roads" (Signposting)**
    * Steve Yegge's "Vibe Coding" book emphasizes that agents get lost in Monoliths.
    * Create a file named `AI_CONTEXT.md` in the root.
    * Scan the `iso20022-migration-service` code structure and write a high-level "Map" of the system in this file. Explain:
        * Where the core logic lives.
        * How the build system works.
        * Key entry points.
    * This file will serve as your "Signpost" for future sessions.

4.  **Establish Agent Rules**
    * Create a `.windsurfrules` file (or append to it) with the following instructions to ensure you always use this memory system:
        """
        # AI BEHAVIOR RULES - BEADS MEMORY SYSTEM
        1. ALWAYS start a session by running `bd issues` to see what work is in progress.
        2. When starting a new task, create it first: `bd create "Task description"`
        3. When a task is done, close it: `bd close <id>`
        4. If you hit a roadblock, comment on the issue: `bd comment <id> "Stuck on..."`
        5. Read `AI_CONTEXT.md` if you are confused about the project structure.
        """

5.  **Finalize**
    * Create a first "Epic" issue for our migration project: `bd create "Initial Setup of ISO20022 Migration Service"`