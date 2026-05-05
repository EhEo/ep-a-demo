"""Alarms router — in-memory store with asyncio background dispatcher."""
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from pydantic import AwareDatetime, BaseModel

router = APIRouter(prefix="/alarms", tags=["alarms"])

_store: dict[int, "Alarm"] = {}
_next_id: int = 1


class AlarmCreate(BaseModel):
    trigger_at: AwareDatetime
    message: str


class Alarm(AlarmCreate):
    id: int
    fired: bool = False


def get_store() -> dict[int, "Alarm"]:
    return _store


@router.post("", response_model=Alarm, status_code=201)
async def create_alarm(body: AlarmCreate, store: Annotated[dict, Depends(get_store)]):
    global _next_id
    alarm = Alarm(id=_next_id, **body.model_dump())
    store[_next_id] = alarm
    _next_id += 1
    return alarm


@router.get("", response_model=list[Alarm])
async def list_alarms(store: Annotated[dict, Depends(get_store)]):
    return list(store.values())


@router.delete("/{alarm_id}", status_code=204)
async def delete_alarm(alarm_id: int, store: Annotated[dict, Depends(get_store)]):
    if alarm_id not in store:
        raise HTTPException(status_code=404, detail="Alarm not found")
    del store[alarm_id]


async def _alarm_dispatcher():
    """Poll every second; log and mark alarms whose trigger_at has passed."""
    while True:
        now = datetime.now(timezone.utc)
        for alarm in list(_store.values()):
            if not alarm.fired and alarm.trigger_at.astimezone(timezone.utc) <= now:
                alarm.fired = True
                print(f"[ALARM] id={alarm.id} message={alarm.message!r}")
        await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_alarm_dispatcher())
    yield
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)
