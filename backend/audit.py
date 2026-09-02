from sqlalchemy.orm import Session
from backend.models import AuditLog

def add_audit_log(
    db: Session,
    case_id: str,
    event_type: str,
    description: str,
    decision: str | None = None,
    result: str | None = None
):
    log = AuditLog(
        case_id=case_id,
        event_type=event_type,
        description=description,
        decision=decision,
        result=result
    )

    db.add(log)
    db.commit()
    return log