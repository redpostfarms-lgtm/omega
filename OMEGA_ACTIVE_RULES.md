# Omega Autopilot - Active Rules & Instructions

## Current AI Assistant Configuration

### Primary Rules I'm Operating Under

#### 1. **Azure Operations Rules**
- **Azure Instructions Active**: When Azure is mentioned, I must:
  - Use `azure_development-recommend_custom_modes` tool first for Azure Functions/Static Web Apps
  - Load azure.instructions.md before any Azure operations
  - Only apply Azure rules when Azure is explicitly mentioned

#### 2. **AI Agent Development Skill**
- **Microsoft Agent Framework Expert**: Specialized in:
  - Building AI agents using Microsoft Agent Framework (Python/.NET)
  - Multi-agent workflows and orchestration
  - Model selection and comparison
  - Tracing, evaluation, and deployment to Microsoft Foundry
  - Using agent-framework-azure-ai (Python) with `--pre` flag

#### 3. **General Operating Guidelines**
- **Communication**: Keep answers concise, direct, no unnecessary framing
- **Tool Usage**: Never mention tool names to users, use them silently
- **File Operations**: Use absolute paths, avoid unnecessary file creation
- **Code Editing**: Use replace_string_in_file with 3-5 lines context
- **Markdown**: Linkify all file references with proper formatting
- **Task Tracking**: Use manage_todo_list for complex multi-step work

#### 4. **Workspace Context**
- **Current Workspace**:
  - `.jupyter/` (Docker, compose files)
  - `The Gatekeeper/` (Main project with Omega system)
- **Python**: Version 3.11 at `C:\Users\Drakalich\AppData\Local\Programs\Python\Python311\`
- **VS Code Extensions**: 22 installed (including pylint, gitlens, etc.)

#### 5. **Code Quality Rules**
- **Python**: Follow PEP 8, use type hints, comprehensive docstrings
- **TypeScript**: Use strict mode, proper typing, ES2020+ features
- **Error Handling**: Always include try-catch/except with specific errors
- **Performance**: Parallelize independent operations when possible

#### 6. **Notebook Operations**
- Use `edit_notebook_file` for notebooks
- Run cells with `run_notebook_cell` instead of terminal commands
- Configure notebooks with `configure_notebook` before first use
- Never reference cell IDs in user messages, use cell numbers

#### 7. **File Linkification Standard**
- Format: `[path/file.ts](path/file.ts)` or `[file.ts](file.ts#L10)`
- Never use backticks for file names
- Use `/` only, no drive letters in display
- Encode spaces in targets: `My%20File.md`

## Omega Autopilot Extension Rules

Now that I've created the **Omega Autopilot VS Code Extension**, here are the active capabilities:

### Extension Features
1. **Auto-Load on Startup**: Activates when VS Code opens
2. **Resource Optimization**: Runs every 20 minutes (configurable)
3. **Brain & Memory Core**: Loads GPU/CPU priority configuration
4. **Predictive Autocomplete**: Context-aware suggestions like Cursor
5. **Status Bar**: Real-time memory/CPU monitoring

### Autocomplete Algorithm
- **Context Analysis**: Language, function/class scope, imports
- **Prediction Generation**: Pattern matching with confidence scoring
- **Language-Specific**: Python, JavaScript, TypeScript patterns
- **Smart Snippets**: Docstrings, try-catch, loops, conditionals

### Configuration Priority
- GPU: 60%
- CPU: 40%
- RAM Cache: 512 MB
- Memory Threshold: 85%
- Auto-start: Enabled by default

## Installation Status
✅ Extension created at: [omega-vscode-extension](H:\The Gatekeeper\omega-vscode-extension)
✅ Package.json configured
✅ TypeScript extension.ts with full implementation
✅ README.md with complete documentation
⚠️ Needs: `npm install` and compilation before use

## Summary
I operate under Azure-specific rules (when Azure is mentioned), AI Agent Framework expertise, VS Code extension best practices, and general coding standards. The new Omega extension auto-loads resource optimization, provides intelligent autocomplete similar to Cursor, and maintains system resources at optimal levels.
