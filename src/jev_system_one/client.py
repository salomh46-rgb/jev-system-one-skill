"""
Jev System One Production Client ⚡
High-throughput, dual-backend decision client supporting native TypeSafe AI and OpenRouter.
Author: Javohirbek Asqarov (Jasper) & Open Source Community
"""

import os
import time
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("jev_system_one")


@dataclass
class QuestionResult:
    name: str
    type: str
    value: Any
    confidence: float = 1.0
    probabilities: Dict[str, float] = field(default_factory=dict)


@dataclass
class DecisionResponse:
    id: str
    model: str
    results: Dict[str, QuestionResult]
    latency_ms: float
    raw: Dict[str, Any] = field(default_factory=dict)


class JevClient:
    """
    Production-grade System One client for Jev (TypeSafe AI).
    Supports Native TypeSafe endpoint and OpenRouter fallback.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        backend: str = "auto",  # 'typesafe', 'openrouter', or 'auto'
        timeout: float = 5.0,
    ):
        self.typesafe_key = api_key or os.getenv("TYPESAFE_API_KEY")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        self.timeout = timeout
        
        if backend == "auto":
            if self.typesafe_key:
                self.backend = "typesafe"
                self.base_url = base_url or os.getenv("TYPESAFE_BASE_URL", "https://api.typesafe.ai/v1")
                self.active_key = self.typesafe_key
            elif self.openrouter_key:
                self.backend = "openrouter"
                self.base_url = "https://openrouter.ai/api/v1"
                self.active_key = self.openrouter_key
            else:
                self.backend = "mock"
                self.base_url = "local"
                self.active_key = "mock"
                logger.warning("No TYPESAFE_API_KEY or OPENROUTER_API_KEY detected. Running in mock simulation mode.")
        else:
            self.backend = backend
            self.base_url = base_url
            self.active_key = api_key

    async def decide_async(
        self,
        state: Dict[str, Any],
        questions: List[Dict[str, Any]],
        model: str = "jev-1.13"
    ) -> DecisionResponse:
        """
        Asynchronously evaluate state against typed questions with sub-100ms latency.
        """
        start_time = time.perf_counter()

        if self.backend == "mock":
            return self._mock_decision(state, questions, start_time)

        try:
            import httpx
            async with httpx.AsyncClient(timeout=self.timeout) as http_client:
                if self.backend == "typesafe":
                    headers = {
                        "Authorization": f"Bearer {self.active_key}",
                        "Content-Type": "application/json",
                        "User-Agent": "JevSystemOne-Client/1.0",
                    }
                    payload = {
                        "model": model,
                        "state": state,
                        "questions": questions,
                    }
                    res = await http_client.post(f"{self.base_url}/systemone", headers=headers, json=payload)
                    res.raise_for_status()
                    data = res.json()
                    return self._parse_typesafe_response(data, start_time)

                elif self.backend == "openrouter":
                    headers = {
                        "Authorization": f"Bearer {self.active_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/salomh46-rgb/jev-system-one-skill",
                        "X-Title": "Jev System One Agent Skill",
                    }
                    # OpenRouter format for typesafe/jev-1.13
                    prompt = (
                        f"State:\n{json.dumps(state, ensure_ascii=False, indent=2)}\n\n"
                        f"Questions:\n{json.dumps(questions, ensure_ascii=False, indent=2)}"
                    )
                    payload = {
                        "model": f"typesafe/{model}",
                        "messages": [{"role": "user", "content": prompt}],
                        "response_format": {"type": "json_object"},
                    }
                    res = await http_client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                    res.raise_for_status()
                    data = res.json()
                    return self._parse_openrouter_response(data, questions, start_time)

        except Exception as e:
            logger.error(f"Error querying Jev backend ({self.backend}): {e}. Falling back to simulation.")
            return self._mock_decision(state, questions, start_time)

    def decide(
        self,
        state: Dict[str, Any],
        questions: List[Dict[str, Any]],
        model: str = "jev-1.13"
    ) -> DecisionResponse:
        """Synchronous wrapper for decide_async."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import nest_asyncio
                nest_asyncio.apply()
                return loop.run_until_complete(self.decide_async(state, questions, model))
            else:
                return loop.run_until_complete(self.decide_async(state, questions, model))
        except RuntimeError:
            return asyncio.run(self.decide_async(state, questions, model))

    def _parse_typesafe_response(self, data: Dict[str, Any], start_time: float) -> DecisionResponse:
        latency = (time.perf_counter() - start_time) * 1000
        results = {}
        for q_name, q_data in data.get("results", {}).items():
            results[q_name] = QuestionResult(
                name=q_name,
                type=q_data.get("type", "unknown"),
                value=q_data.get("value"),
                confidence=q_data.get("confidence", 1.0),
                probabilities=q_data.get("probabilities", {}),
            )
        return DecisionResponse(
            id=data.get("id", f"dec_{int(time.time()*1000)}"),
            model=data.get("model", "jev-1.13"),
            results=results,
            latency_ms=round(latency, 2),
            raw=data,
        )

    def _parse_openrouter_response(
        self, data: Dict[str, Any], questions: List[Dict[str, Any]], start_time: float
    ) -> DecisionResponse:
        latency = (time.perf_counter() - start_time) * 1000
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content) if isinstance(content, str) else content
        
        results = {}
        for q in questions:
            name = q["name"]
            val = parsed.get(name)
            # Normalize structure
            if isinstance(val, dict):
                results[name] = QuestionResult(
                    name=name,
                    type=q.get("type", "choice"),
                    value=val.get("value", val.get("choice")),
                    confidence=val.get("confidence", 0.95),
                    probabilities=val.get("probabilities", {}),
                )
            else:
                results[name] = QuestionResult(
                    name=name,
                    type=q.get("type", "choice"),
                    value=val,
                    confidence=0.96,
                )

        return DecisionResponse(
            id=data.get("id", f"dec_or_{int(time.time()*1000)}"),
            model=data.get("model", "typesafe/jev-1.13"),
            results=results,
            latency_ms=round(latency, 2),
            raw=data,
        )

    def _mock_decision(
        self, state: Dict[str, Any], questions: List[Dict[str, Any]], start_time: float
    ) -> DecisionResponse:
        """Fast deterministic local fallback simulation when offline."""
        latency = (time.perf_counter() - start_time) * 1000
        results = {}
        for q in questions:
            name = q["name"]
            q_type = q.get("type", "choice")
            if q_type == "choice":
                options = q.get("options", ["DEFAULT"])
                results[name] = QuestionResult(
                    name=name,
                    type="choice",
                    value=options[0],
                    confidence=0.975,
                    probabilities={opt: (0.975 if i == 0 else 0.025 / max(1, len(options) - 1)) for i, opt in enumerate(options)}
                )
            elif q_type == "noul":
                results[name] = QuestionResult(
                    name=name,
                    type="noul",
                    value=True,
                    confidence=0.98,
                )
            elif q_type == "score":
                results[name] = QuestionResult(
                    name=name,
                    type="score",
                    value=round((q.get("min", 0) + q.get("max", 10)) / 2, 2),
                    confidence=0.92,
                )

        return DecisionResponse(
            id=f"dec_mock_{int(time.time()*1000)}",
            model="jev-mock-simulation",
            results=results,
            latency_ms=round(latency, 2),
        )
