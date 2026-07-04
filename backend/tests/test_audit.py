from jwbuddy.security.audit import AuditLogger
import tempfile
import os


def test_audit_write_and_query():
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
        log_path = f.name
    logger = AuditLogger(log_path)
    logger.log(user="tester", action="test", detail="hello")
    logs = logger.query(limit=10)
    assert len(logs) >= 1
    assert logs[-1]["action"] == "test"
    os.unlink(log_path)
