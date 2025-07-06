from __future__ import annotations

import os
import re
from typing import List
from openai import OpenAI
from dotenv import load_dotenv

from agent_voting_system import Agent  

load_dotenv()

class ChatGPTAgent(Agent):
    """An `Agent` powered by the OpenAI ChatCompletion API."""

    def __init__(
        self,
        name: str,
        domain: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.2,
    ) -> None:
        super().__init__(name, domain)
        self.model = model
        self.temperature = temperature
        self._client = OpenAI()
        self._client = OpenAI() if os.getenv("OPENAI_API_KEY") else None

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------
    def _chat(self, messages: list[dict[str, str]], max_tokens: int = 256) -> str:
        """Call the OpenAI chat completion endpoint and return *raw* content.

        Falls back to returning an empty string if the OpenAI client is not
        available so that the caller can degrade gracefully.
        """

        if not self._client:
            return ""  # Trigger fallback handling upstream

        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

    # ------------------------------------------------------------------
    # Public API – overrides of `Agent`
    # ------------------------------------------------------------------
    def propose(self, task: str) -> str:  # type: ignore[override]
        """Create a proposal for *task* using GPT-4o (or fallback)."""
        if not self._client:
            # Environment not set up – keep previous behaviour.
            return super().propose(task)

        system_prompt = (
            f"You are {self.name}, an expert in {self.domain}. "
            "Draft a concise proposal (one sentence) that solves the "
            "following task."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task},
        ]
        proposal = self._chat(messages)
        # Ensure we always return some content
        return proposal if proposal else super().propose(task)

    def vote(self, proposals: List[str]) -> str:  # type: ignore[override]
        """Select the best proposal using GPT-4o (or fallback)."""
        if not self._client:
            return super().vote(proposals)

        formatted = "\n".join(f"{i+1}. {p}" for i, p in enumerate(proposals))
        system_prompt = (
            f"You are {self.name}, an expert in {self.domain}. "
            "You are participating in a blind vote. "
            "Choose the *number* of the proposal you believe is strongest "
            "given the task context. Respond with ONLY that number."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    "Here are the proposals:\n" + formatted + "\n" +
                    "Which proposal is best?"
                ),
            },
        ]
        answer = self._chat(messages, max_tokens=5)

        # Extract the first integer from the response – fall back if invalid.
        match = re.search(r"\d+", answer)
        if match:
            idx = int(match.group()) - 1  # 1-based → 0-based
            if 0 <= idx < len(proposals):
                return proposals[idx]

        return super().vote(proposals) 