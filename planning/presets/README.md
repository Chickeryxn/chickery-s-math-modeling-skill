# Optional presets

A preset is an explicitly activated, versioned set of defaults. It is advisory configuration, not a source of human decisions or problem semantics.

Every preset should declare:

```json
{
  "preset_id": "example",
  "version": "1.0.0",
  "activation": "explicit",
  "authority": "advisory",
  "defaults": {}
}
```

Rules:

- A preset must be explicitly activated and recorded in the run snapshot.
- A preset may provide defaults but may not silently create decisions.
- A preset may not override the active problem model contract or a human decision.
- A preset may not contain historical problem results or frozen numbers.
- `references/` is advisory knowledge and is not an automatic requirement for a new problem.
