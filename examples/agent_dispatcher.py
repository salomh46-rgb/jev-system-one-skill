"""
Example: Autonomous Multi-Agent Routing with Jev System One ⚡
Demonstrates sub-100ms task dispatching to specialized subagents.
"""

import sys
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.append(str(Path(__file__).parent.parent / "scripts"))

from jev_client import JevClient

def route_agent_tasks():
    client = JevClient()

    tasks = [
        "Ushbu kodda SQL injection yoki secret kalit sizib chiqish xavfi bormi?",
        "Tizimga yangi xaridor kelganda uning balansi 0 bo'lishi bo'yicha unit testlar yozib ber",
        "Oxirgi 24 soat ichida TypeSafe AI Jev modeli haqidagi barcha yangi maqolalarni top",
        "React interfeysidagi knopka animatsiyasini DaisyUI bilan yangila",
    ]

    print("=" * 70)
    print("🤖 JEV AUTONOMOUS AGENT DISPATCHER BENCHMARK")
    print("=" * 70)

    for task in tasks:
        state = {"task_description": task}
        questions = [
            {
                "name": "target_agent",
                "type": "choice",
                "options": ["SECURITY_AUDITOR", "TEST_ENGINEER", "RESEARCH", "FRONTEND_DEV", "GENERAL"]
            },
            {
                "name": "is_read_only",
                "type": "noul"
            }
        ]

        decision = client.decide(state=state, questions=questions)
        agent = decision.results["target_agent"]
        read_only = decision.results["is_read_only"]

        print(f"Topshiriq: \"{task}\"")
        print(f"  -> Yo'naltirilgan Agent: [{agent.value}] (Ishonch: {agent.confidence * 100:.1f}%)")
        print(f"  -> Read-only muhitmi?: {read_only.value}")
        print(f"  -> Qaror vaqti: {decision.latency_ms} ms")
        print("-" * 70)

if __name__ == "__main__":
    route_agent_tasks()
