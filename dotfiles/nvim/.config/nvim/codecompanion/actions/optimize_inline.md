---
name: Optimize code (inline)
interaction: inline
description: Optimize the selected code
opts:
  alias: optimize_inline
  is_slash_cmd: true
  modes:
    - v
  auto_submit: true
---

## system

You are a senior ${context.filetype} developer. Optimize the provided code for better performance and readability. Return ONLY the optimized code without explanations, markdown formatting, or code blocks.

## user

${context.code}
