# Documentation Standards

## Docstrings
- Required for all public classes, methods, and functions
- Include: purpose, parameters, return values, exceptions
- Follow Sphinx/Google style consistently

## Comments

### Brief Overview
These rules govern code comments and documentation standards. Focus is on keeping code clean and avoiding unhelpful or redundant comments.

### Comment Guidelines

- **Keep helpful TODOs**: Preserve actionable TODO comments that clearly indicate work needed
  - Example: `# TODO: Implement via market data adapter`
  - Example: `# TODO: Add get_recent_trade_outcomes method to transaction service`

- **Remove historical/context comments**: Delete comments that explain where code came from or past refactoring history
  - ❌ BAD: `(merged from agent/portfolio.py)`
  - ❌ BAD: `NOTE: This function was previously in utils/old_file.py`
  - ❌ BAD: `This method has been refactored to remove direct SQLite access`

- **No explanatory NOTE comments**: Do not add NOTE comments during refactoring that merely state what was done
  - ❌ BAD: `NOTE: This function requires market data adapter that provides historical bars. It no longer uses direct database access.`
  - ✅ GOOD: Keep the docstring simple and focused on current behavior

- **Docstrings should be current**: Focus on what the function does NOW, not what it used to do or how it changed
  - ✅ GOOD: "Calculate pairwise correlation between all symbols."
  - ❌ BAD: "Calculate pairwise correlation between all symbols. NOTE: This function has been refactored..."

### Code Cleanliness

- Code should be self-documenting where possible
- Comments that don't add value should be removed
- Historical context belongs in git history, not in code comments
- If a comment doesn't help someone using or maintaining the code, it shouldn't be there

### Basic Standards

- Place above code, not beside (except brief end-of-line comments)
- Avoid obvious statements
- Start with capital letter, end with period
- Update when code changes

## Markdown Files
- Professional senior dev tone
- Clear, concise, direct
- No fluff or filler words
- Proper syntax and formatting
- No third-person references

## Documentation Tasks
- Create ModelContextProtocol for accessing code indices
- Structure documentation with clear sections and headings
- Enable quick reference and navigation
- Provide clear explanations of functionality, purpose, and usage
