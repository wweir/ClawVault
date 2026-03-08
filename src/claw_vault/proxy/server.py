"""Proxy server management: start/stop mitmproxy with ClawVaultAddon."""

from __future__ import annotations

import asyncio
import threading
from typing import Optional, Callable

import structlog

from claw_vault.config import Settings
from claw_vault.proxy.interceptor import ClawVaultAddon
from claw_vault.detector.engine import DetectionEngine
from claw_vault.guard.rule_engine import RuleEngine
from claw_vault.sanitizer.replacer import Sanitizer
from claw_vault.sanitizer.restorer import Restorer
from claw_vault.monitor.token_counter import TokenCounter

logger = structlog.get_logger()


class ProxyServer:
    """Manages the mitmproxy transparent proxy lifecycle."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._thread: Optional[threading.Thread] = None
        self._master = None

        # Initialize shared components
        self.token_counter = TokenCounter()
        self.sanitizer = Sanitizer()
        self.restorer = Restorer()
        self.detection_engine = DetectionEngine()
        self.rule_engine = RuleEngine(
            mode=settings.guard.mode,
            auto_sanitize=settings.guard.auto_sanitize,
        )

        self.addon = ClawVaultAddon(
            detection_engine=self.detection_engine,
            rule_engine=self.rule_engine,
            sanitizer=self.sanitizer,
            restorer=self.restorer,
            token_counter=self.token_counter,
            intercept_hosts=settings.proxy.intercept_hosts,
        )

    def set_audit_callback(self, callback: Callable, main_loop: asyncio.AbstractEventLoop) -> None:
        """Wire an async audit callback from the main event loop.

        Since mitmproxy runs in a background thread (sync), we use
        ``asyncio.run_coroutine_threadsafe`` to bridge the gap.
        """
        def _threadsafe_callback(record, scan=None):
            asyncio.run_coroutine_threadsafe(callback(record, scan), main_loop)

        self.addon.audit_callback = _threadsafe_callback

    def start(self) -> None:
        """Start the proxy server in a background thread."""
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info(
            "proxy_started",
            host=self._settings.proxy.host,
            port=self._settings.proxy.port,
        )

    def _run(self) -> None:
        """Run mitmproxy in the background thread."""
        from mitmproxy.options import Options
        from mitmproxy.tools.dump import DumpMaster

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        opts = Options(
            listen_host=self._settings.proxy.host,
            listen_port=self._settings.proxy.port,
            ssl_insecure=not self._settings.proxy.ssl_verify,
        )

        async def run_master():
            self._master = DumpMaster(opts)
            self._master.addons.add(self.addon)
            try:
                await self._master.run()
            except Exception as e:
                logger.error("proxy_error", error=str(e))

        loop.run_until_complete(run_master())

    def stop(self) -> None:
        """Stop the proxy server."""
        if self._master:
            self._master.shutdown()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        logger.info("proxy_stopped")
