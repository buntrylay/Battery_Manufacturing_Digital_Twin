# from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# # Define the registry for all metrics
# REGISTRY = CollectorRegistry()

# # Define the application metrics
# machine_status = Gauge("machine_status", "Machine status", ["machine"], registry=REGISTRY)
# jobs_completed = Counter("machine_jobs_completed_total", "Jobs completed", ["machine"], registry=REGISTRY)
# job_duration = Histogram("machine_job_duration_seconds", "Job duration", ["machine"], registry=REGISTRY)

# # Mapping example for metrics
# def set_machine_status(machine_id: str, status: int):
#     machine_status.labels(machine=machine_id).set(status)

# def inc_job_completed(machine_id: str):
#     jobs_completed.labels(machine=machine_id).inc()

# def observe_job_duration(machine_id: str, duration: float):
#     job_duration.labels(machine=machine_id).observe(duration)