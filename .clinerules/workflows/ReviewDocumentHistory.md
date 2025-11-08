{
  "name": "Document Project from Conversation Memory",
  "description": "Reviews the entire conversation history and creates comprehensive documentation of the project, including all steps, configurations, commands, challenges, gotchas, and solutions",
  "version": "1.0.0",
  "steps": [
    {
      "type": "task",
      "text": "Review the memory from this entire conversation and identify:\n\n1. **Project Overview**: What was built? What is the main purpose/goal?\n2. **Technology Stack**: Programming languages, frameworks, libraries, tools used\n3. **Initial Setup Steps**: Environment setup, dependency installation, configuration files created\n4. **All Commands Executed**: Every terminal command, package installation, script execution\n5. **File Structure**: Directory structure and key files created\n6. **Configuration Changes**: All .env files, config files, settings modified\n7. **Code Components**: Major classes, functions, modules developed\n8. **Development Steps**: Chronological order of what was built and when\n9. **Challenges & Gotchas**: Every error encountered, bug fixed, blocker resolved\n10. **Solutions Applied**: How each challenge was resolved, including code fixes\n11. **API Integrations**: External services connected, API keys needed, authentication setup\n12. **Deployment Steps**: How the project was deployed or prepared for deployment\n13. **Testing Approach**: Tests written, testing strategies used\n14. **Best Practices**: Design patterns, architectural decisions, coding standards followed\n15. **Lessons Learned**: Key insights and recommendations for future development\n\nCreate a comprehensive markdown blog post that documents ALL of this information in detail, organized with clear sections and subsections."
    },
    {
      "type": "task",
      "text": "Structure the documentation as follows:\n\n# [Project Name]: Complete Development Documentation\n\n## Table of Contents\n- Executive Summary\n- Technology Stack\n- Prerequisites\n- Initial Setup\n- Development Journey\n- Challenges & Solutions\n- Final Architecture\n- Deployment Guide\n- Lessons Learned\n- Appendix (all commands, all configurations)\n\nEnsure EVERY step is documented with:\n- The exact command or code used\n- Why it was needed\n- What problem it solved\n- Any errors encountered and how they were fixed"
    },
    {
      "type": "task",
      "text": "For the 'Commands & Configuration' section, create a complete reference that includes:\n\n### Installation Commands\n```bash\n# List every npm install, pip install, or other package manager command\n```\n\n### Configuration Files\n```\n# Show the contents of .env, config files, etc.\n```\n\n### Build & Run Commands\n```bash\n# Every command needed to build and run the project\n```\n\n### Deployment Commands\n```bash\n# Commands used for deployment\n```"
    },
    {
      "type": "task",
      "text": "For the 'Challenges & Solutions' section, document every issue in this format:\n\n### Challenge #X: [Brief Description]\n**When it occurred:** [At what stage of development]\n**Error message:** \n```\n[Exact error if applicable]\n```\n**Root cause:** [Why this happened]\n**Solution:** [Step-by-step fix]\n**Code changes:** \n```language\n[Exact code that fixed it]\n```\n**Prevention:** [How to avoid this in future]"
    },
    {
      "type": "task",
      "text": "Include a 'Quick Start Guide' section that allows someone to recreate the entire project from scratch using ONLY the information in this document. It should include:\n\n1. Prerequisites checklist\n2. Step-by-step setup (every single command in order)\n3. Configuration (every file that needs to be created/modified)\n4. Verification steps (how to test each component works)\n5. Common issues and their fixes\n6. Next steps for further development"
    },
    {
      "type": "task",
      "text": "Add a 'Code Architecture' section with:\n\n- System design diagram (describe in text/ASCII)\n- Data flow explanation\n- Key design decisions and rationale\n- Directory structure with explanations\n- Major components and their responsibilities\n- How components interact with each other"
    },
    {
      "type": "task",
      "text": "Create an 'Evolution Timeline' section showing:\n\n### Phase 1: Initial Setup\n- [Date/Session]: Initial project creation\n- [Date/Session]: Dependency installation\n- [Date/Session]: Basic structure setup\n\n### Phase 2: Core Development\n- [Date/Session]: Feature X implemented\n- [Date/Session]: Integration Y completed\n\n### Phase 3: Refinement\n- [Date/Session]: Bug fixes and optimizations\n- [Date/Session]: Testing and validation\n\n### Phase 4: Deployment\n- [Date/Session]: Deployment preparation\n- [Date/Session]: Production deployment"
    },
    {
      "type": "task",
      "text": "Save the complete documentation as a markdown file named:\n`[project-name]-complete-development-guide.md`\n\nEnsure it is:\n- Comprehensive (covers EVERYTHING from the conversation)\n- Well-organized (clear hierarchy and structure)\n- Actionable (someone can follow it to recreate the project)\n- Detailed (includes all commands, code snippets, configurations)\n- Professional (formatted like a technical blog post)\n\nThe document should be at least 5000 words and serve as a complete reference for the entire development process."
    }
  ]
}
