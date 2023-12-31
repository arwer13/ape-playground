from .common import validate_events_chain


def validate_beacon_report_receiver_set_event(event, callback: str):
    _events_chain = ["LogScriptCall", "BeaconReportReceiverSet"]

    validate_events_chain([e.name for e in event], _events_chain)

    assert event.count("BeaconReportReceiverSet") == 1

    assert event["BeaconReportReceiverSet"]["callback"] == callback


def validate_oracle_member_added(event, new_member: str):
    _events_chain = ["LogScriptCall", "MemberAdded"]

    validate_events_chain([e.name for e in event], _events_chain)

    assert event.count("MemberAdded") == 1

    assert event["MemberAdded"]["member"] == new_member


def validate_oracle_quorum_changed(event, new_quorum: int):
    _events_chain = ["LogScriptCall", "QuorumChanged"]

    validate_events_chain([e.name for e in event], _events_chain)

    assert event.count("QuorumChanged") == 1

    assert event["QuorumChanged"]["quorum"] == new_quorum
