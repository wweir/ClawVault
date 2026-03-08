"""Local rule engine for determining actions based on detection results."""

from __future__ import annotations

import structlog

from claw_vault.detector.engine import ScanResult, ThreatLevel
from claw_vault.guard.action import Action, ActionResult

logger = structlog.get_logger()


class RuleEngine:
    """Evaluates scan results and determines the appropriate action.

    Modes:
    - strict: BLOCK all detected threats (sensitive data, injections, commands)
    - interactive: auto-sanitize sensitive data, block injections, warn commands
    - permissive: log all threats, allow everything (sanitize if auto_sanitize on)

    auto_sanitize: replace sensitive data with masked placeholders and restore
    in AI response.  Only applies in interactive/permissive modes.
    """

    def __init__(self, mode: str = "interactive", auto_sanitize: bool = True) -> None:
        self._mode = mode
        self._auto_sanitize = auto_sanitize

    def evaluate(self, scan: ScanResult) -> ActionResult:
        """Determine action based on scan results and current mode."""
        if not scan.has_threats:
            return ActionResult(
                action=Action.ALLOW,
                reason="No threats detected",
                risk_score=0.0,
                details=[],
            )

        threat = scan.threat_level
        score = scan.max_risk_score
        details = self._build_details(scan)

        has_injections = bool(scan.injections)
        has_commands = bool(scan.commands)
        has_sensitive_only = bool(scan.sensitive) and not has_injections and not has_commands

        if self._mode == "strict":
            return self._strict_evaluate(threat, score, details, scan)
        elif self._mode == "permissive":
            return self._permissive_evaluate(threat, score, details, scan, has_sensitive_only)
        else:
            return self._interactive_evaluate(threat, score, details, scan, has_injections, has_commands, has_sensitive_only)

    def _strict_evaluate(
        self, threat: ThreatLevel, score: float, details: list[str], scan: ScanResult,
    ) -> ActionResult:
        # Strict: block ALL threats — sensitive data, injections, commands
        return ActionResult(Action.BLOCK, "Strict mode: threat blocked", score, details)

    def _interactive_evaluate(
        self, threat: ThreatLevel, score: float, details: list[str], scan: ScanResult,
        has_injections: bool, has_commands: bool, has_sensitive_only: bool,
    ) -> ActionResult:
        # Injections always blocked
        if has_injections:
            return ActionResult(Action.BLOCK, "Prompt injection blocked", score, details)
        # Sensitive data: auto-sanitize if enabled, otherwise warn
        if has_sensitive_only and scan.sensitive:
            if self._auto_sanitize:
                return ActionResult(Action.SANITIZE, "Sensitive data auto-sanitized", score, details)
            return ActionResult(Action.ASK_USER, "Sensitive data detected — enable auto-sanitize for masking", score, details)
        # Dangerous commands: warn
        if has_commands:
            return ActionResult(Action.ASK_USER, "Dangerous command detected — review needed", score, details)
        # Mixed threats
        if scan.sensitive and self._auto_sanitize:
            return ActionResult(Action.SANITIZE, "Sensitive data auto-sanitized", score, details)
        return ActionResult(Action.ASK_USER, "Threats detected — review needed", score, details)

    def _permissive_evaluate(
        self, threat: ThreatLevel, score: float, details: list[str], scan: ScanResult,
        has_sensitive_only: bool,
    ) -> ActionResult:
        if has_sensitive_only and scan.sensitive and self._auto_sanitize:
            return ActionResult(Action.SANITIZE, "Sensitive data auto-sanitized (permissive)", score, details)
        return ActionResult(Action.ALLOW, "Permissive mode: allowed with logging", score, details)

    @staticmethod
    def _build_details(scan: ScanResult) -> list[str]:
        details: list[str] = []
        for s in scan.sensitive:
            details.append(f"Sensitive: {s.description} ({s.masked_value})")
        for c in scan.commands:
            details.append(f"Command: {c.reason} — `{c.command[:40]}`")
        for i in scan.injections:
            details.append(f"Injection: {i.description}")
        return details
