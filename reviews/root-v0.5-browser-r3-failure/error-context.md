# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: game.spec.ts >> final strike saves outcome immediately, blocks stale commands and resumes canonical result
- Location: tests/browser/game.spec.ts:120:1

# Error details

```
Error: browserContext.close: ENOENT: no such file or directory, open '/workspace/Roguelike-deckbuilder/test-results/.playwright-artifacts-0/traces/8b1bb1493a64c9fc3ab6-eb1b1cb54da9ecf47c5e-recording14.network'
```