from typing import NamedTuple
from utils.config import ZERO_ADDRESS

from .common import validate_events_chain

class StETH_burn_requested(NamedTuple):
    requestedBy: str
    amountOfStETH: int
    amountOfShares: int
    isCover: bool

def validate_burn_requested_event(event, b: StETH_burn_requested):
    _events_chain = ["LogScriptCall", "LogScriptCall", "Approval", "Transfer", "TransferShares", "StETHBurnRequested", "ScriptResult"]

    validate_events_chain([e.name for e in event], _events_chain)

    assert event.count("LogScriptCall") == 2
    assert event.count("StETHBurnRequested") == 1

    assert event["StETHBurnRequested"]["amountOfStETH"] == b.amountOfStETH
    assert event["StETHBurnRequested"]["amountOfShares"] == b.amountOfShares
    assert event["StETHBurnRequested"]["requestedBy"] == b.requestedBy
    assert event["StETHBurnRequested"]["isCover"] == b.isCover