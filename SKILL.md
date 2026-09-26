---
name: jev-system-one
description: >
  High-speed, non-autoregressive decision engine and sub-100ms routing skill powered by TypeSafe AI's Jev model ("System One").
  Use when: sub-100ms intent classification, agent/subagent routing, boolean decision guardrails, spam/fraud detection,
  triage and state classification without token-generation overhead, deterministic structured decisions, or integrating
  TypeSafe AI / OpenRouter `typesafe/jev-1.13` into Python and TypeScript backend pipelines.
compatibility: Works with Python (typesafe-sdk, httpx) and Node.js/TypeScript (@typesafe-ai/sdk, fetch). Compatible with native TypeSafe API and OpenRouter.
---

# Jev System One Decision Engine ⚡

Production-grade skill for integrating **TypeSafe AI's Jev ("System One")** model into autonomous agent workflows, Telegram bots (`@Ovozli_SavdoBOT`, `@DentaMedKlinika_bot`), and high-throughput backend APIs.

Unlike conversational LLMs ("System Two") that generate prose token-by-token with multi-second latency, **Jev evaluates arbitrary state against typed questions in parallel**, returning structured choices, boolean conditions (`noul`), and calibrated confidence scores in **70ms – 250ms** at **$0.042/1M input tokens** (0 output token cost).

---

## 🚀 When to Use This Skill

Activate `jev-system-one` when any of the following capabilities are required:
1. **Ultra-Fast Intent Classification:** Route user messages to the right handler before hitting heavy LLMs.
2. **Autonomous Multi-Agent Routing:** Decide which subagent (`research`, `code-reviewer`, `security-auditor`, `test-engineer`) to invoke in <100ms.
3. **Execution Guardrails & Safety:** Instant Boolean (`noul`) validation: *Is this tool call safe?*, *Is this input an injection attack?*
4. **Data Extraction & Categorization:** Classify unstructured tickets, logs, voice-transcribed transactions into strict enums without JSON parsing errors.
5. **Cost Optimization:** Replace 80% of small classification LLM calls with Jev, reducing API expenses by over 95%.

---

## 🔑 Environment Variables (.env)

```bash
# Option A: Native TypeSafe AI
TYPESAFE_API_KEY="ts_live_xxxxxxxxxxxxxxxxxxxx"
TYPESAFE_BASE_URL="https://api.typesafe.ai/v1"

# Option B: OpenRouter Fallback / Universal Access
OPENROUTER_API_KEY="sk-or-v1-xxxxxxxxxxxxxxxxxxxx"
```

---

## 🧱 Core Decision Primitives

Jev evaluates three fundamental typed question primitives:

| Primitive | Description | Output Structure |
| :--- | :--- | :--- |
| **`choice`** | Selects exactly one winning option from a discrete set | `{ value: "OPTION_B", confidence: 0.985, probabilities: {...} }` |
| **`noul`** | High-precision Boolean (True / False / Null) verification | `{ value: true, probability: 0.991 }` |
| **`score`** | Continuous or discrete rating on a bounded scale | `{ value: 8.5, confidence: 0.92 }` |

---

## 🐍 Python Implementation (FastAPI / Aiogram 3 / Standalone)

Use `scripts/jev_client.py` for a battle-tested, asynchronous client with automatic fallback:

```python
import asyncio
from jev_client import JevClient

async def main():
    client = JevClient() # Automatically picks TYPESAFE_API_KEY or OPENROUTER_API_KEY

    # 1. State representing the incoming context (e.g. Telegram message, user action)
    state = {
        "text": "Bugun Dilshod akaga 450 ming so'mlik dori qarzga berildi",
        "sender_role": "cashier",
        "source": "telegram_voice_stt"
    }

    # 2. Parallel typed questions
    questions = [
        {
            "name": "intent",
            "type": "choice",
            "options": ["QARZ_BERISH", "NAQD_SAVDO", "XARAJAT", "MIJOZ_SAVOLI", "NOMALUM"]
        },
        {
            "name": "is_urgent",
            "type": "noul"
        }
    ]

    # 3. Decision executed in ~85ms!
    decision = await client.decide(state=state, questions=questions)
    
    print(f"Tanlangan Intent: {decision.results['intent'].value}")
    print(f"Ishonch foizi: {decision.results['intent'].confidence * 100:.1f}%")
    print(f"Shoshilinchmi: {decision.results['is_urgent'].value}")
    print(f"Kechikish (Latency): {decision.latency_ms} ms")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## ⚡ TypeScript / Next.js Implementation

```typescript
import { JevDecisionEngine } from "./jev_router";

const jev = new JevDecisionEngine({
  apiKey: process.env.TYPESAFE_API_KEY || process.env.OPENROUTER_API_KEY!,
});

export async function routeUserPrompt(prompt: string) {
  const result = await jev.evaluate({
    state: { prompt },
    questions: [
      {
        name: "target_subagent",
        type: "choice",
        options: ["CODE_REVIEWER", "TEST_ENGINEER", "SECURITY_AUDITOR", "GENERAL_CHAT"],
      },
      {
        name: "requires_filesystem_write",
        type: "noul",
      },
    ],
  });

  // Guardrail with Calibrated Confidence
  if (result.target_subagent.confidence > 0.90) {
    return result.target_subagent.value;
  }
  return "GENERAL_CHAT"; // Graceful fallback
}
```

---

## 🛡️ Senior Production Invariants & Guardrails

1. **Always Calibrate with Confidence Thresholds:** Never trust uncalibrated output. Always define an operational gate:
   ```python
   if decision.results["intent"].confidence < 0.80:
       # Fallback to general LLM reasoning or prompt user for clarification
       return fallback_to_gemini(state)
   ```
2. **Dual-Backend Resiliency:** If native TypeSafe API experiences any latency degradation, fail over seamlessly to OpenRouter (`typesafe/jev-1.13`).
3. **Zero Secret Leakage:** Never hardcode API keys. Use `os.getenv("TYPESAFE_API_KEY")` and register in `.env.example`.
4. **Zero Output Token Waste:** Jev emits zero prose tokens. Latency remains fixed regardless of prompt size up to 32k tokens.
