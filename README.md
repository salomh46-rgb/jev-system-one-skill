# ⚡ Jev System One — Sub-100ms Decision Engine & Agent Skill

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![Latency: 70ms](https://img.shields.io/badge/latency-70ms--150ms-brightgreen.svg)]()
[![TypeSafe AI](https://img.shields.io/badge/TypeSafe%20AI-Jev%201.13-purple.svg)](https://typesafe.ai)
[![OpenRouter Ready](https://img.shields.io/badge/OpenRouter-Compatible-orange.svg)](https://openrouter.ai)

**The first production-grade Agent Skill and SDK for TypeSafe AI's Jev ("System One") non-autoregressive decision model.**

*Stop making 3-second conversational LLM calls for simple decisions. Execute typed classifications, booleans, and guardrails in 70 milliseconds at $0.042/1M tokens with zero output cost.*

[Quickstart](#-quickstart) • [Why System One?](#-why-system-one-the-kahneman-shift) • [Python SDK](#-python-sdk) • [TypeScript SDK](#-typescript-sdk) • [Agent Skill](#-agent-skill-integration) • [Benchmarks](#-benchmarks)

</div>

---

## 🧠 Why "System One"? (The Kahneman Shift)

Nobel laureate Daniel Kahneman divided cognition into two distinct systems:
* **System 2 (Slow & Deliberative):** Free-form prose, multi-step math, research, creative writing. *(Today's LLMs: GPT-4, Claude, Gemini)*
* **System 1 (Fast & Intuitive):** Instant pattern recognition, categorical decisions, boolean reflexes, intent routing. *(TypeSafe AI's Jev)*

```
Traditional Stack (Slow & Costly):
User Request ──► [ Heavy LLM (GPT/Claude/Gemini) ] ──► (2500ms, $0.003, JSON syntax risk)

Modern System 1 + System 2 Stack (Sub-100ms):
User Request ──► [ JEV (System One) ] ──(70ms, $0.00004)──► Structured Decision
                        │
       Is heavy reasoning needed?
        ├── NO  ──► Instant Response / Database Action (Done in 80ms!)
        └── YES ──► Route to Specialized System 2 LLM
```

---

## 📊 Benchmarks vs Traditional LLMs

| Metric | Traditional LLM (GPT-4o / Claude 3.5 / Gemini) | Jev System One (`jev-1.13`) | Gain |
| :--- | :--- | :--- | :--- |
| **Response Latency** | `1,500ms – 4,000ms` | **`70ms – 180ms`** | **~25x Faster** |
| **Input Cost (1M tokens)** | `$2.50 – $5.00` | **`$0.042`** | **98% Cheaper** |
| **Output Token Cost** | `$10.00 – $15.00` | **`$0.00 (Always Free)`** | **100% Free** |
| **Output Predictability** | Token-by-token (Hallucination risk) | **Strictly Typed Enums & Booleans** | **100% Deterministic** |
| **Calibrated Confidence** | Post-hoc softmax (poorly calibrated) | **RLCD Native Confidence (0.0 - 1.0)** | **Reliable Gatekeeping** |

---

## ⚡ Quickstart

### 1. Installation

#### Python:
```bash
pip install jev-system-one
# Or clone and install locally:
pip install -e .
```

#### TypeScript / Node.js:
```bash
npm install jev-system-one
```

### 2. Environment Setup

Create a `.env` file with either your native TypeSafe API key or OpenRouter key:

```bash
# Option A: Native TypeSafe AI
TYPESAFE_API_KEY="ts_live_xxxxxxxxxxxxxxxxxxxx"

# Option B: OpenRouter (Universal Instant Access)
OPENROUTER_API_KEY="sk-or-v1-xxxxxxxxxxxxxxxxxxxx"
```

---

## 🐍 Python SDK

### Ultra-Fast Intent Classification (<100ms)

```python
import asyncio
from jev_system_one import JevClient

async def main():
    client = JevClient() # Automatically auto-detects TypeSafe or OpenRouter

    state = {
        "user_message": "Akrom akaga 350 ming qarzga sement yuklab yubordik",
        "sender_channel": "telegram_bot"
    }

    questions = [
        {
            "name": "intent",
            "type": "choice",
            "options": ["QARZ_BERISH", "NAQD_SAVDO", "XARAJAT", "SAVOL", "BOSHQA"]
        },
        {
            "name": "is_urgent",
            "type": "noul" # High-precision boolean
        }
    ]

    # Evaluates in ~85ms!
    decision = await client.decide_async(state=state, questions=questions)

    print(f"Intent: {decision.results['intent'].value}")
    print(f"Confidence: {decision.results['intent'].confidence * 100:.1f}%")
    print(f"Urgent: {decision.results['is_urgent'].value}")
    print(f"Latency: {decision.latency_ms} ms")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🌐 TypeScript SDK

### Next.js / Express / Edge Middleware

```typescript
import { JevDecisionEngine } from "jev-system-one";

const jev = new JevDecisionEngine();

export async function middleware(req: Request) {
  const body = await req.json();

  const decision = await jev.evaluate({
    state: { payload: body },
    questions: [
      {
        name: "is_prompt_injection",
        type: "noul",
      },
      {
        name: "priority_tier",
        type: "choice",
        options: ["ENTERPRISE", "GROWTH", "FREE"],
      },
    ],
  });

  // Guardrail check in <80ms
  if (decision.is_prompt_injection.value && decision.is_prompt_injection.confidence > 0.90) {
    return new Response(JSON.stringify({ error: "Suspicious payload rejected." }), { status: 400 });
  }

  // Route to priority queue...
}
```

---

## 🤖 Agent Skill Integration

This repository is an official, ready-to-use **Agent Skill** for **Antigravity**, **Claude Code**, and **Cowork**.

### Adding to your Agent Ecosystem:
Simply copy the `SKILL.md` into your `.agents/skills/jev-system-one/` folder:

```bash
mkdir -p .agents/skills/jev-system-one
cp SKILL.md .agents/skills/jev-system-one/
```

Your autonomous agents will automatically use Jev to:
1. **Route tasks between subagents** (`research`, `code-reviewer`, `security-auditor`) in 70ms.
2. **Pre-flight guardrails** before executing high-risk file modifications or terminal commands.
3. **Filter high-volume event streams** without wasting conversational tokens.

---

## 🧩 Core Primitives

Jev operates on three fundamental decision primitives:

1. **`choice`**: Selects exactly one label from a predefined set of choices with probability distributions.
2. **`noul`**: Evaluates conditions with strict boolean calibration (`true` / `false` / `null`).
3. **`score`**: Predicts quantitative indices (e.g. sentiment score 1-10, risk rating 0-100).

---

## 🛡️ Production Standards

* **Zero-Secret-Leakage:** Strictly enforces `.env` configuration; rejects hardcoded tokens.
* **Calibrated RLCD Thresholds:** Native programmatic gatekeeping:
  ```python
  if decision.results["intent"].confidence < 0.85:
      return route_to_human_or_system2_llm()
  ```
* **Offline Mock Simulation:** Seamlessly falls back to instant local mock when running without an internet connection or test suites.

---

## 🤝 Contributing

Contributions are warmly welcome! Please open an issue or submit a pull request.
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'feat: Add AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

Developed with ❤️ by **Javohirbek Asqarov (Jasper)** and the global open-source AI community.
