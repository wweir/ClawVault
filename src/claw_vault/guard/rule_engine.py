"""Local rule engine for determining actions based on detection results."""

from __future__ import annotations

import structlog

from claw_vault.detector.engine import ScanResult, ThreatLevel
from claw_vault.guard.action import Action, ActionResult
from claw_vault.guard.rules_store import RuleConfig, RuleCondition, load_rules

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
        # Custom rules loaded from ~/.ClawVault/rules.yaml
        # The dashboard can update this at runtime.
        self._rules: list[RuleConfig] = load_rules()

    # -------- Public configuration helpers --------

    @property
    def rules(self) -> list[RuleConfig]:
        return list(self._rules)

    def set_rules(self, rules: list[RuleConfig]) -> None:
        """Replace in-memory rules (used by dashboard API)."""
        self._rules = list(rules)

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

        # 1) Custom rules: if any enabled rule matches, it takes precedence
        if self._rules:
            custom_result = self._evaluate_custom_rules(scan, details)
            if custom_result is not None:
                return custom_result

        # 2) Fallback to built-in mode matrix behaviour
        has_injections = bool(scan.injections)
        has_commands = bool(scan.commands)
        has_sensitive_only = bool(scan.sensitive) and not has_injections and not has_commands

        if self._mode == "strict":
            return self._strict_evaluate(threat, score, details, scan)
        elif self._mode == "permissive":
            return self._permissive_evaluate(threat, score, details, scan, has_sensitive_only)
        else:
            return self._interactive_evaluate(threat, score, details, scan, has_injections, has_commands, has_sensitive_only)

    # -------- Built-in guard matrix evaluation --------

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

    # -------- Custom rule evaluation --------

    def _evaluate_custom_rules(self, scan: ScanResult, details: list[str]) -> ActionResult | None:
        """Evaluate user-defined rules from rules.yaml.

        The first enabled rule whose condition matches the scan wins.
        If no rule matches, returns None so the built-in logic can decide.
        """
        for rule in self._rules:
            if not rule.enabled:
                continue
            cond: RuleCondition = rule.when
            try:
                if not self._matches_condition(cond, scan):
                    continue
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("guard.rules.eval_error", rule_id=rule.id, error=str(exc))
                continue

            # Map string action from RuleConfig to Action enum
            try:
                action = Action(rule.action)
            except ValueError:
                logger.warning("guard.rules.invalid_action", rule_id=rule.id, action=rule.action)
                continue

            logger.info(
                "guard.rules.matched",
                rule_id=rule.id,
                rule_name=rule.name,
                action=action.value,
                max_risk_score=scan.max_risk_score,
            )
            return ActionResult(
                action=action,
                reason=f"Rule '{rule.name}' matched",
                risk_score=scan.max_risk_score,
                details=details,
            )

        return None

    @staticmethod
    def _matches_condition(cond: RuleCondition, scan: ScanResult) -> bool:
        """Check if a rule condition matches a given scan result."""
        has_sensitive = bool(scan.sensitive)
        has_commands = bool(scan.commands)
        has_injections = bool(scan.injections)

        if cond.has_sensitive is not None and cond.has_sensitive != has_sensitive:
            return False
        if cond.has_commands is not None and cond.has_commands != has_commands:
            return False
        if cond.has_injections is not None and cond.has_injections != has_injections:
            return False

        if cond.threat_levels is not None:
            if scan.threat_level.value not in cond.threat_levels:
                return False

        if cond.min_risk_score is not None:
            if scan.max_risk_score < cond.min_risk_score:
                return False

        if cond.pattern_types:
            matched = False
            # Sensitive detections: pattern_type
            for s in scan.sensitive:
                if s.pattern_type in cond.pattern_types:
                    matched = True
                    break
            # Command detections: reason as a "type"-like identifier
            if not matched:
                for c in scan.commands:
                    if c.reason in cond.pattern_types:
                        matched = True
                        break
            # Injection detections: injection_type
            if not matched:
                for i in scan.injections:
                    if i.injection_type in cond.pattern_types:
                        matched = True
                        break
            if not matched:
                return False

        return True

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
