# Git Configuration & Hooks - Developer Guide

Welcome to SmartOps Core! This guide explains the Git configuration and pre-commit hooks used in this project.

## Quick Start (5 minutes)

### Windows (PowerShell)
```powershell
# 1. Run the setup script
.\setup-git-config.ps1

# 2. If prompted to install PSScriptAnalyzer
Install-Module -Name PSScriptAnalyzer -Force

# 3. You're done! Pre-commit hooks are now active
```

### macOS/Linux (Bash)
```bash
# 1. Run the setup script
bash setup-git-config.sh

# 2. You're done! Pre-commit hooks are now active
```

## What These Files Do

### Configuration Files

| File | Purpose | For Whom |
|------|---------|----------|
| `.gitattributes` | Normalizes line endings (Windows vs Unix) | Git |
| `.psanalyzerrules.psd1` | PowerShell code quality rules | Git pre-commit hook |
| `.editorconfig` | Editor formatting consistency | VS Code, Visual Studio, etc. |
| `.gitignore` | Files to exclude from Git | Git |

### Validation Scripts

| File | Purpose | Usage |
|------|---------|-------|
| `validate-scripts.ps1` | Manual validation before committing | `.\validate-scripts.ps1` |
| `pre-commit` | Automatic validation (Bash) | Runs automatically before commit |
| `pre-commit.ps1` | Automatic validation (PowerShell) | Runs automatically before commit |

### Setup & Documentation

| File | Purpose |
|------|---------|
| `setup-git-config.ps1` | Automated setup for Windows developers |
| `setup-git-config.sh` | Automated setup for macOS/Linux developers |
| `GIT_CONFIG_RULES.md` | Detailed configuration documentation |
| `HOOKS_INSTALL_GUIDE.md` | Manual installation guide |

## Key Rules to Remember

### 1. ✅ Avoid PowerShell Automatic Variables
```powershell
# WRONG - Will be rejected by pre-commit hook
$Error = "Red"
$Warning = "Yellow"
$Success = "Green"
$Info = "Cyan"

# CORRECT - Use these names instead
$ErrorColor = "Red"
$WarningColor = "Yellow"
$SuccessColor = "Green"
$InfoColor = "Cyan"
```

### 2. ✅ Use Consistent Line Endings
- All code files use LF (Unix style), not CRLF (Windows style)
- Git automatically converts them - you don't need to do anything!
- `.gitattributes` handles this automatically

### 3. ✅ Keep Code Clean
- No trailing whitespace
- No merge conflict markers
- Valid syntax in Python and PowerShell

## What Happens When You Commit

```
$ git commit -m "your message"

[Pre-commit hook runs]
  ✓ Checks PowerShell automatic variables
  ✓ Checks for non-ASCII characters
  ✓ Validates Python syntax
  ✓ Checks for trailing whitespace
  ✓ Checks for merge conflict markers

[If all checks pass]
  ✓ Commit succeeds

[If any check fails]
  ✗ Commit is rejected with error message
  ✗ You must fix the issue and try again
```

## Common Scenarios

### Scenario 1: Pre-commit hook rejected my commit
```
ERROR: Found automatic variable assignment
Use alternative names like: ErrorColor, WarningColor, SuccessColor, InfoColor
```

**Solution:** Rename the variable and try again
```powershell
# Change: $Error = "Red"  →  $ErrorColor = "Red"
git add .
git commit -m "your message"
```

### Scenario 2: "Non-ASCII character found"
```
ERROR: Found non-ASCII character (byte: 225)
```

**Solution:** Remove special characters (accents, emojis, etc.)
- Remove Spanish accents: á → a, é → e, etc.
- Remove emojis: ✅ → Remove
- Keep code 100% ASCII

### Scenario 3: Python syntax error
```
ERROR: Syntax error in file
```

**Solution:** Validate manually and fix
```bash
python -m py_compile path/to/file.py
# Fix the error and try again
git add .
git commit -m "your message"
```

### Scenario 4: "Bypass" the hook (not recommended)
```bash
git commit --no-verify -m "your message"
```

⚠️ **Warning:** Only use this in emergencies! The hook exists to catch issues early.

## Manual Validation

Before committing, you can validate manually:

```powershell
# Validate all scripts
.\validate-scripts.ps1

# Validate only PowerShell
.\validate-scripts.ps1 -Type powershell

# Validate only Python
.\validate-scripts.ps1 -Type python
```

## Advanced: Using PSScriptAnalyzer Directly

```powershell
# Install PSScriptAnalyzer
Install-Module -Name PSScriptAnalyzer -Force

# Analyze a single file
Invoke-ScriptAnalyzer -Path ".\routers\demo.py" -Settings ".\.psanalyzerrules.psd1"

# Analyze all PowerShell files
Invoke-ScriptAnalyzer -Path ".\*.ps1" -Settings ".\.psanalyzerrules.psd1" -Recurse
```

## Troubleshooting

### Pre-commit hook not running
```bash
# Check if hook is installed
ls -la .git/hooks/pre-commit

# If missing, reinstall
bash setup-git-config.sh  # macOS/Linux
.\setup-git-config.ps1   # Windows
```

### "Cannot find module PSScriptAnalyzer"
```powershell
# Install it
Install-Module -Name PSScriptAnalyzer -Force

# Verify installation
Get-Module -ListAvailable PSScriptAnalyzer
```

### Hook permissions issue (macOS/Linux)
```bash
chmod +x .git/hooks/pre-commit
```

### Need to reconfigure Git settings
```bash
git config core.autocrlf false
git config core.safecrlf warn
git config core.hooksPath .git/hooks
```

## Team Standards

All developers in SmartOps Core must follow these standards:

1. **Run the setup script** before making your first commit
2. **Review `GIT_CONFIG_RULES.md`** to understand all rules
3. **Never bypass the hook** without explicit approval
4. **Keep code 100% English** (Spanish only in `.md` documentation)
5. **Use ASCII characters only** in source code
6. **Validate before committing** using `validate-scripts.ps1`

## CI/CD Integration

These same rules run in our CI/CD pipeline:
- GitHub Actions validates all PRs
- Failed validation blocks merge
- All developers must pass the same checks

## Questions?

1. Check `GIT_CONFIG_RULES.md` for detailed configuration info
2. Check `HOOKS_INSTALL_GUIDE.md` for installation details
3. See `GIT_SETUP_SUMMARY.md` for technical overview
4. Ask your team lead or project maintainer

## References

- **PowerShell Variables:** [Microsoft Docs](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_automatic_variables)
- **Git Hooks:** [Git Documentation](https://git-scm.com/docs/githooks)
- **PSScriptAnalyzer:** [GitHub Repository](https://github.com/PowerShell/PSScriptAnalyzer)
- **EditorConfig:** [EditorConfig.org](https://editorconfig.org/)

---

## APPENDIX: Git Configuration Details

### 1. `.gitattributes`

Defines how Git handles different file types regarding line endings and binary formats.

**Key configurations:**
- **PowerShell files** (`.ps1`, `.ps1xml`, `.psd1`, `.psm1`): LF line endings
- **Python files** (`.py`, `.pyw`): LF line endings
- **Documentation** (`.md`, `.markdown`, `.txt`): LF line endings
- **Docker files**: LF line endings
- **JSON files**: LF line endings
- **Shell scripts** (`.sh`): LF line endings
- **Binary files** (`.pdf`, `.png`, `.jpg`, `.zip`, `.exe`, `.dll`): Binary format

**Purpose:** Ensures consistent line endings across all systems (Windows, macOS, Linux) and prevents merge conflicts.

### 2. `.psanalyzerrules.psd1`

PowerShell Script Analyzer configuration file for code quality rules.

**Key rules enabled:**
- `PSAvoidAssignmentToAutomaticVariable`: Prevents assignment to automatic variables like `$Error`, `$Warning`, `$Success`
- `PSAvoidUsingWriteHost`: Disabled for test scripts (colored output acceptable)
- `PSProvideCommentHelp`: Disabled for test scripts
- `PSUseApprovedVerbs`: Function names use approved PowerShell verbs
- `PSAvoidUsingCmdletAliases`: Requires full cmdlet names (e.g., `Get-ChildItem` not `gci`)

**Severity levels:** Error and Warning

**Purpose:** Maintains code quality standards and prevents common PowerShell anti-patterns.

### 3. `.editorconfig`

Editor configuration file for consistent formatting across different editors and IDEs.

**Key configurations:**
- **Charset:** UTF-8 for all files
- **Line endings:** LF for cross-platform compatibility
- **Python files:** 4-space indentation, 100-character line limit
- **PowerShell files:** 4-space indentation, LF line endings
- **JSON/YAML files:** 2-space indentation
- **Markdown files:** No trailing whitespace trimming (content preservation)

**Purpose:** Ensures code formatting consistency regardless of which editor developers use.

### 4. `.gitignore`

Specifies files and directories to exclude from Git tracking.

**Key sections:**
- **PowerShell:** `*.ps1.bak`, `*.ps1.tmp`, `PSScriptAnalyzerResults.json`
- **Python:** `__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `.coverage`
- **Environment & secrets:** `.env`, `.env.local`
- **IDE & OS:** `.vscode/`, `.idea/`, `.DS_Store`, `Thumbs.db`

**Purpose:** Prevents committing unnecessary files to the repository.

### Variable Naming Conventions

To avoid PowerShell Analyzer warnings:

**Automatic Variables to Avoid:**
- `$Error` → Use `$ErrorColor`, `$ErrorList`, `$ErrorObj`
- `$Warning` → Use `$WarningColor`, `$WarningList`
- `$Success` → Use `$SuccessColor`, `$SuccessFlag`
- `$Info` → Use `$InfoColor`, `$InfoData`
- `$Output` → Use `$OutputData`, `$OutputResult`
- `$Matches` → Use `$MatchResult`, `$MatchData`

### Line Ending Normalization

When cloning the repository on Windows:
```bash
git config core.autocrlf false
git config core.safecrlf warn
```

This ensures `.gitattributes` rules are respected.

### Using PSScriptAnalyzer Locally

```powershell
# Install PSScriptAnalyzer
Install-Module -Name PSScriptAnalyzer -Force

# Analyze a single file
Invoke-ScriptAnalyzer -Path ".\run_tests.ps1" -Settings ".\.psanalyzerrules.psd1"

# Analyze all PowerShell files
Invoke-ScriptAnalyzer -Path ".\*.ps1" -Settings ".\.psanalyzerrules.psd1" -Recurse
```

### Continuous Integration

These configurations help CI/CD pipelines:

1. **Consistent formatting:** All developers use same rules
2. **Code quality:** PSScriptAnalyzer prevents common issues
3. **Merge conflict prevention:** Consistent line endings reduce conflicts
4. **Cross-platform support:** LF line endings work on all systems

### Best Practices

1. **Always use `$ErrorActionPreference = "Stop"`** in PowerShell scripts
2. **Use full cmdlet names**, not aliases (e.g., `Get-ChildItem` not `gci`)
3. **Validate scripts** before committing: `Invoke-ScriptAnalyzer -Path file.ps1`
4. **Use approved verbs** when writing functions
5. **Document complex logic** with comments
6. **Test on multiple platforms** when possible

---

**Last Updated:** December 1, 2025  
**Version:** 1.1 (merged GIT_CONFIG_RULES)  
**Status:** Production Ready ✓
