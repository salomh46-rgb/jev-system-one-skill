"""
Example: Ultra-Fast Intent Classification with Jev System One ⚡
Demonstrates routing e-commerce voice messages in <100ms.
"""

import sys
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

from jev_client import JevClient

def run_test():
    client = JevClient()

    test_cases = [
        "Jasur akaga bugun 500 ming qarzga sement berildi",
        "Kassada qancha pul qoldi? Hisobotni ko'rsat",
        "Bugun tushlikka va benzinga 85 ming xarajat qildik",
        "Salom, do'koningiz soat nechagacha ochiq?",
    ]

    print("=" * 65)
    print("🚀 JEV SYSTEM ONE: INTENT CLASSIFICATION BENCHMARK")
    print("=" * 65)

    for text in test_cases:
        state = {"user_input": text}
        questions = [
            {
                "name": "intent",
                "type": "choice",
                "options": ["QARZ_BERISH", "KASSA_HISOBOT", "XARAJAT", "SAVOL_CHAT", "BOSHQA"]
            },
            {
                "name": "requires_balance_update",
                "type": "noul"
            }
        ]

        decision = client.decide(state=state, questions=questions)
        
        intent = decision.results["intent"]
        balance = decision.results["requires_balance_update"]

        print(f"Xabar: \"{text}\"")
        print(f"  -> Qaror: {intent.value} (Ishonch: {intent.confidence * 100:.1f}%)")
        print(f"  -> Balans o'zgaradimi?: {balance.value}")
        print(f"  -> Kechikish: {decision.latency_ms} ms | Model: {decision.model}")
        print("-" * 65)

if __name__ == "__main__":
    run_test()
