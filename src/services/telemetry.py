import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Callable, Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.events import (
    UserPromptEvent,
    ToolDecisionEvent,
    ToolResultEvent,
    ApiRequestEvent,
    ApiErrorEvent,
)
from src.models.telemetry import TelemetryLog
from src.repositories.telemetry import TelemetryRepository
from src.schemas.telemetry import (
    TelemetryLogSchema,
    UsageOverviewSchema,
    ActivityOverTimeSchema,
    CostBreakdownSchema,
    ToolUsageSchema,
    ErrorAnalysisSchema,
    TerminalBreakdownSchema,
    EventDistributionSchema,
)


class TelemetryService:
    """Service layer handling business logic for Telemetry Logs."""

    def __init__(self, session: AsyncSession):
        self.repository = TelemetryRepository(session)

    async def get_usage_overview(self) -> UsageOverviewSchema:
        return await self.repository.get_usage_overview()

    async def get_activity_over_time(self) -> List[ActivityOverTimeSchema]:
        return await self.repository.get_activity_over_time()

    async def get_cost_breakdown(self) -> List[CostBreakdownSchema]:
        return await self.repository.get_cost_breakdown()

    async def get_tool_usage(self) -> ToolUsageSchema:
        return await self.repository.get_tool_usage()

    async def get_error_analysis(self) -> List[ErrorAnalysisSchema]:
        return await self.repository.get_error_analysis()

    async def get_terminal_breakdown(self) -> List[TerminalBreakdownSchema]:
        return await self.repository.get_terminal_breakdown()

    async def get_event_type_distribution(self) -> List[EventDistributionSchema]:
        return await self.repository.get_event_type_distribution()

    def _parse_event_base(self, log: TelemetryLog) -> Dict[str, Any]:
        """Parses common event attributes, ensuring timezone-aware timestamps."""
        attrs = log.attributes or {}
        raw_ts = attrs.get("event.timestamp")
        
        if raw_ts:
            dt = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
        else:
            dt = datetime.now(timezone.utc)
            
        # Ensure it's timezone-aware
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
            
        return {
            "log_id": log.id,
            "employee_email": log.employee_email,
            "session_id": attrs.get("session.id", "unknown"),
            "event_timestamp": dt,
            "terminal_type": attrs.get("terminal.type"),
        }

    async def _process_user_prompt(self, log: TelemetryLog):
        base = self._parse_event_base(log)
        attrs = log.attributes or {}
        event = UserPromptEvent(
            **base,
            prompt_length=int(attrs.get("prompt_length", 0))
        )
        await self.repository.add(event)

    async def _process_tool_decision(self, log: TelemetryLog):
        base = self._parse_event_base(log)
        attrs = log.attributes or {}
        event = ToolDecisionEvent(
            **base,
            tool_name=attrs.get("tool_name", "unknown"),
            decision=attrs.get("decision", "unknown"),
            source=attrs.get("source", "unknown")
        )
        await self.repository.add(event)

    async def _process_tool_result(self, log: TelemetryLog):
        base = self._parse_event_base(log)
        attrs = log.attributes or {}
        event = ToolResultEvent(
            **base,
            tool_name=attrs.get("tool_name", "unknown"),
            success=str(attrs.get("success", "false")).lower() == "true",
            decision_type=attrs.get("decision_type"),
            decision_source=attrs.get("decision_source"),
            duration_ms=int(attrs.get("duration_ms", 0)),
            tool_result_size_bytes=int(attrs.get("tool_result_size_bytes", 0)) if attrs.get("tool_result_size_bytes") else None
        )
        await self.repository.add(event)

    async def _process_api_request(self, log: TelemetryLog):
        base = self._parse_event_base(log)
        attrs = log.attributes or {}
        cost_usd = attrs.get("cost_usd")
        event = ApiRequestEvent(
            **base,
            model=attrs.get("model", "unknown"),
            input_tokens=int(attrs.get("input_tokens", 0)),
            output_tokens=int(attrs.get("output_tokens", 0)),
            cache_read_tokens=int(attrs.get("cache_read_tokens", 0)) if attrs.get("cache_read_tokens") else None,
            cache_creation_tokens=int(attrs.get("cache_creation_tokens", 0)) if attrs.get("cache_creation_tokens") else None,
            cost_usd=float(cost_usd) if cost_usd else None,
            duration_ms=int(attrs.get("duration_ms", 0))
        )
        await self.repository.add(event)

    async def _process_api_error(self, log: TelemetryLog):
        base = self._parse_event_base(log)
        attrs = log.attributes or {}
        event = ApiErrorEvent(
            **base,
            model=attrs.get("model", "unknown"),
            error=attrs.get("error", "unknown"),
            status_code=attrs.get("status_code"),
            attempt=int(attrs.get("attempt", 0)),
            duration_ms=int(attrs.get("duration_ms", 0))
        )
        await self.repository.add(event)

    async def seed_telemetry(self, file_path: Path, batch_size: int = 1000) -> None:
        """Seeds telemetry log data into the database using batch processing."""
        if not file_path.exists():
            logger.error(f"Telemetry file {file_path} not found.")
            raise FileNotFoundError(f"Telemetry file {file_path} not found.")

        dispatch_map = {
            "claude_code.user_prompt": self._process_user_prompt,
            "claude_code.tool_decision": self._process_tool_decision,
            "claude_code.tool_result": self._process_tool_result,
            "claude_code.api_request": self._process_api_request,
            "claude_code.api_error": self._process_api_error,
        }

        logger.info(f"Seeding telemetry from {file_path} in batches of {batch_size}...")
        try:
            batch_logs = []
            total_processed = 0
            with file_path.open(mode="r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        for log_entry in data.get("logEvents", []):
                            msg = json.loads(log_entry.get("message", "{}"))
                            
                            raw_ts = msg.get("attributes", {}).get("timestamp")
                            parsed_ts = None
                            if raw_ts:
                                try:
                                    if isinstance(raw_ts, str):
                                        parsed_ts = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
                                    else:
                                        parsed_ts = raw_ts
                                except ValueError:
                                    logger.warning(f"Invalid timestamp format: {raw_ts}. Using None.")

                            schema_data = {
                                "employee_email": msg.get("attributes", {}).get("user.email", "unknown@example.com"),
                                "timestamp": parsed_ts,
                                "body": msg.get("body", ""),
                                "attributes": msg.get("attributes", {}),
                                "scope": msg.get("scope", {}),
                                "resource": msg.get("resource", {})
                            }
                            
                            valid_data = TelemetryLogSchema(**schema_data)
                            db_log = TelemetryLog(**valid_data.model_dump())
                            
                            # Add to current batch
                            batch_logs.append((db_log, msg))
                            total_processed += 1
                            
                            # If batch is full, process it
                            if len(batch_logs) >= batch_size:
                                logger.info(f"Processing batch of {len(batch_logs)}... (Total processed: {total_processed})")
                                await self._process_batch(batch_logs, dispatch_map)
                                batch_logs = []

                    except json.JSONDecodeError as e:
                        logger.warning(f"JSON decode error on line {line_num}: {e}. Skipping.")
                    except Exception as e:
                        logger.error(f"Error processing telemetry line {line_num}: {e}. Skipping.")
            
            # Process remaining logs
            if batch_logs:
                logger.info(f"Processing final batch of {len(batch_logs)}... (Total processed: {total_processed})")
                await self._process_batch(batch_logs, dispatch_map)

            logger.info(f"Finished seeding {total_processed} telemetry logs.")
        except Exception as e:
            logger.error(f"Failed to read telemetry file {file_path}: {e}")
            raise

    async def _process_batch(self, batch: List[tuple], dispatch_map: Dict[str, Callable]) -> None:
        """Processes a batch of telemetry logs and their specialized events."""
        for db_log, msg in batch:
            await self.repository.add(db_log)
        
        # Flush to assign IDs to TelemetryLog entries
        await self.repository.session.flush()

        for db_log, msg in batch:
            body = db_log.body
            if body in dispatch_map:
                try:
                    await dispatch_map[body](db_log)
                except Exception as e:
                    logger.error(f"Error processing specialized event {body} for log {db_log.id}: {e}")
            else:
                logger.warning(f"Unknown event body type: {body}. Skipping row.")
        
        await self.repository.session.flush()
        await self.repository.commit()
