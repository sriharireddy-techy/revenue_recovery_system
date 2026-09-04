from backend.state_machine import can_transition

def test_failed_to_analyzing():
    assert can_transition(
        "FAILED",
        "ANALYZING"
    )


def test_success_cannot_recover():
    assert not can_transition(
        "SUCCESS",
        "RECOVERING"
    )


def test_closed_cannot_change():
    assert not can_transition(
        "CLOSED",
        "RECOVERING"
    )