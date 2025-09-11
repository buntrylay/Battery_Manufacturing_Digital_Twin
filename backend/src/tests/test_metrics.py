# tests/test_metrics.py
from metrics.metrics import REGISTRY, set_machine_status, inc_job_completed, observe_job_duration, ENABLE
import os

def test_metrics_expose_basic_values(monkeypatch):
    monkeypatch.setenv("ENABLE_METRICS", "true")
    set_machine_status("Mixing", 1)
    inc_job_completed("Mixing")
    observe_job_duration("Mixing", 12.3)
    blob = REGISTRY.collect()
    # basic sanity: registry has our metrics families
    names = {m.name for m in blob}
    assert "machine_status" in names
    assert "machine_jobs_completed" in names
    assert "machine_job_duration_seconds" in names
