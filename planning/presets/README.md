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

## Network allowlist (optional, advisory example)

本仓库不编码 offline/network 策略（AGENTS.md）。若你的环境需要，可在此放一个显式激活的 preset，例如：

```json
{
  "preset_id": "network-allowlist-2026",
  "version": "1.0.0",
  "activation": "explicit",
  "authority": "advisory",
  "defaults": {
    "network_allow": ["官方规则页/当年公告", "DOI 解析", "文献真实性核验", "工作流脚本更新"],
    "network_deny": ["检索他人对本题的解法", "下载模板论文直接改编"]
  }
}
```

它只约束 agent 的行为建议，不强制执行（与环境/用户级策略一致）。
