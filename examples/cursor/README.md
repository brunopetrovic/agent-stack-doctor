# Cursor Editor Integration Example

When working with AI coding editors like Cursor, it is helpful to establish rules that keep your agent configurations clean.

By placing a `.cursorrules` file in the root of your repository, you instruct Cursor's AI model to never output placeholder code (like `API_KEY=YOUR_KEY_HERE`) and to always validate configurations before concluding task execution.

## Files in this Example
- `.cursorrules`: A custom configuration file telling Cursor how to align with `agent-stack-doctor` rules.

## Setup in your project

1. Copy `.cursorrules` to the root of your project:
   ```bash
   cp .cursorrules ../../
   ```
2. When prompting Cursor, the editor's model will automatically read `.cursorrules` and use `agent-doctor` to verify code correctness.
