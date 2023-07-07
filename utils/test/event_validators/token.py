from typing import NamedTuple
from utils.config import ZERO_ADDRESS

from .common import validate_events_chain

class Approve(NamedTuple):
    owner: str
    spender: str
    amount: int

def validate_approval_event(event, a: Approve):
    _events_chain = ["LogScriptCall", "LogScriptCall", "Approval", "ScriptResult"]

    validate_events_chain([e.name for e in event], _events_chain)

    assert event.count("LogScriptCall") == 2
    assert event.count("Approval") == 1

    assert event["Approval"]["owner"] == a.owner
    assert event["Approval"]["spender"] == a.spender
    assert event["Approval"]["value"] == a.amount