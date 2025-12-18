import json
import os
import platform
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np


def _now_ms() -> int:
    return int(datetime.now().timestamp() * 1000)


@dataclass
class DebugConfig:
    enabled: bool
    level: str
    save_artifacts: bool
    base_dir: str
    run_id: str
    run_dir: str
    dump_cooldown_ms: int = 1500
    max_screenshots: int = 250
    max_state_dumps: int = 250
    max_exception_dumps: int = 50
    thumb_size: Optional[int] = None
    diff_threshold: Optional[float] = None

    @staticmethod
    def from_config(config: Any) -> "DebugConfig":
        enabled = bool(getattr(config, "debug", False))
        level = getattr(config, "debug_level", "info") if enabled else "off"
        if level not in {"off", "info", "trace"}:
            level = "info" if enabled else "off"
        save_artifacts = getattr(config, "debug_save_artifacts", True)
        base_dir = getattr(config, "debug_dir", "debug")
        dump_cooldown_ms = getattr(config, "debug_dump_cooldown_ms", 1500)
        max_screenshots = getattr(config, "debug_max_screenshots", 250)
        max_state_dumps = getattr(config, "debug_max_state_dumps", 250)
        max_exception_dumps = getattr(config, "debug_max_exception_dumps", 50)
        run_id = (
            datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{os.getpid()}"
            if enabled
            else ""
        )
        run_dir = str(Path(base_dir) / "runs" / run_id) if enabled else ""
        return DebugConfig(
            enabled=enabled,
            level=level,
            save_artifacts=bool(save_artifacts),
            base_dir=str(base_dir),
            run_id=run_id,
            run_dir=run_dir,
            dump_cooldown_ms=int(dump_cooldown_ms),
            max_screenshots=int(max_screenshots),
            max_state_dumps=int(max_state_dumps),
            max_exception_dumps=int(max_exception_dumps),
        )


class NullRecorder:
    enabled = False
    run_dir = ""

    def event(self, name: str, **fields: Any) -> None:
        return

    def metric(self, name: str, **fields: Any) -> None:
        return

    def dump_state(
        self, board: Any, tag: str, loop_id: Optional[int] = None
    ) -> None:
        return

    def dump_exception(
        self,
        exc: Exception,
        tag: str,
        loop_id: Optional[int] = None,
        **context: Any,
    ) -> None:
        return

    def close(self, reason: str, loop_id: Optional[int] = None) -> None:
        return


class DebugRecorder:
    enabled = True

    def __init__(self, cfg: DebugConfig):
        self.cfg = cfg
        self.run_dir = cfg.run_dir
        assert "/runs/" in self.run_dir.replace("\\", "/")
        self._base_path = Path(self.run_dir)
        self._events_path = self._base_path / "events.jsonl"
        self._metrics_path = self._base_path / "metrics.jsonl"
        self._last_dump_ms_by_tag: Dict[str, int] = {}
        self._screenshots_written = 0
        self._state_written = 0
        self._exceptions_written = 0
        self._artifact_cap_hit = False

        screens_dir = self._base_path / "screens"
        state_dir = self._base_path / "state"
        exceptions_dir = self._base_path / "exceptions"

        for path in (self._base_path, screens_dir, state_dir, exceptions_dir):
            path.mkdir(parents=True, exist_ok=True)

        self._write_run_meta()

    def _write_run_meta(self) -> None:
        meta: Dict[str, Any] = {
            "created_at": datetime.now().isoformat(),
            "run_id": self.cfg.run_id,
            "run_dir": self.cfg.run_dir,
            "base_dir": self.cfg.base_dir,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
            "level": self.cfg.level,
            "save_artifacts": self.cfg.save_artifacts,
            "dump_cooldown_ms": self.cfg.dump_cooldown_ms,
            "max_screenshots": self.cfg.max_screenshots,
            "max_state_dumps": self.cfg.max_state_dumps,
            "max_exception_dumps": self.cfg.max_exception_dumps,
        }
        for key in ("thumb_size", "diff_threshold"):
            value = getattr(self.cfg, key, None)
            if value is not None:
                meta[key] = value

        meta_path = self._base_path / "run_meta.json"
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2))

    def event(self, name: str, **fields: Any) -> None:
        payload = {"t_ms": _now_ms(), "name": name}
        payload.update(fields)
        line = json.dumps(payload, ensure_ascii=False)
        with open(self._events_path, "a") as f:
            f.write(line + "\n")

    def metric(self, name: str, **fields: Any) -> None:
        payload = {"t_ms": _now_ms(), "name": name}
        payload.update(fields)
        line = json.dumps(payload, ensure_ascii=False)
        with open(self._metrics_path, "a") as f:
            f.write(line + "\n")

    def _can_dump(self, tag: str, kind: str) -> bool:
        if not self.cfg.save_artifacts:
            return False
        if self._artifact_cap_hit:
            return False

        now = _now_ms()
        last = self._last_dump_ms_by_tag.get(f"{kind}:{tag}")
        if last is not None and now - last < self.cfg.dump_cooldown_ms:
            return False

        cap_hit = False
        if kind == "screen" and self._screenshots_written >= self.cfg.max_screenshots:
            cap_hit = True
        elif kind == "state" and self._state_written >= self.cfg.max_state_dumps:
            cap_hit = True
        elif kind == "exc" and self._exceptions_written >= self.cfg.max_exception_dumps:
            cap_hit = True

        if cap_hit:
            self._artifact_cap_hit = True
            self.event("artifact_cap_reached", kind=kind, tag=tag)
            return False

        self._last_dump_ms_by_tag[f"{kind}:{tag}"] = now
        return True

    def dump_state(
        self, board: Any, tag: str, loop_id: Optional[int] = None
    ) -> None:
        if not self._can_dump(tag, kind="state"):
            return

        loop_str = f"loop_{loop_id}_" if loop_id is not None else ""
        suffix = f"{loop_str}{tag}"
        if self._artifact_cap_hit:
            return

        if hasattr(board, "save_screenshot") and self._can_dump(tag, kind="screen"):
            screen_path = self._base_path / "screens" / f"{suffix}.png"
            try:
                board.save_screenshot(str(screen_path))
                self._screenshots_written += 1
            except Exception:
                pass
        if self._artifact_cap_hit:
            return

        state_written = False
        fen_path = self._base_path / "state" / f"{suffix}_fen.txt"
        try:
            fen_lines = []
            if getattr(board, "board", None) is not None:
                fen_lines.append(str(board.board.fen()))
                fen_lines.append(f"turn_var={board.turn}")
                fen_lines.append(f"our_turn={board.is_our_turn()}")
                fen_lines.append(
                    "moves=" + " ".join([m.uci() for m in board.board.move_stack])
                )
            fen_path.write_text("\n".join(fen_lines))
            state_written = True
        except Exception:
            pass

        if self.cfg.level == "trace":
            if hasattr(board, "pos") and isinstance(board.pos, np.ndarray):
                try:
                    np.save(
                        self._base_path / "state" / f"{suffix}_pos.npy", board.pos
                    )
                except Exception:
                    pass

            if hasattr(board, "prev_pos") and isinstance(board.prev_pos, np.ndarray):
                try:
                    np.save(
                        self._base_path / "state" / f"{suffix}_prev_pos.npy",
                        board.prev_pos,
                    )
                except Exception:
                    pass

        if state_written:
            self._state_written += 1

    def dump_exception(
        self,
        exc: Exception,
        tag: str,
        loop_id: Optional[int] = None,
        **context: Any,
    ) -> None:
        self.event("exception", tag=tag, loop=loop_id, exc=str(exc), **context)

        if not self._can_dump(tag, kind="exc"):
            return

        loop_str = f"loop_{loop_id}_" if loop_id is not None else ""
        suffix = f"{loop_str}{tag}"
        path = self._base_path / "exceptions" / f"{suffix}.txt"

        lines = [
            f"exception_type={type(exc).__name__}",
            f"message={exc}",
            "traceback:",
            traceback.format_exc(),
        ]
        if context:
            try:
                lines.append("context:")
                lines.append(json.dumps(context, indent=2))
            except Exception:
                pass

        try:
            path.write_text("\n".join(lines))
            self._exceptions_written += 1
        except Exception:
            pass

    def close(self, reason: str, loop_id: Optional[int] = None) -> None:
        self.event("exit", reason=reason, loop=loop_id)
