import logging
import time
import requests
from prometheus_client import start_http_server, Gauge
import docker
import tempo_healthcheck


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# list of services where health is determined via HTTP
HTTP_CHECK_SERVICES = {"tempo": tempo_healthcheck.check_tempo_comprehensive}

# ------------------------
# Prometheus metric
# ------------------------
# 1 = healthy, 0 = unhealthy
SERVICE_HEALTH = Gauge("service_health", "1 if service is healthy, 0 if unhealthy", ["service"])

# ------------------------
# Connect to Docker daemon
# ------------------------
client = docker.from_env()

# ------------------------
# Scrape loop
# ------------------------
SCRAPE_INTERVAL = 3  # seconds


def update_metrics():
    containers = client.containers.list(all=True)
    for container in containers:
        name = container.name

        # First, check if this service needs HTTP healthcheck
        if name in HTTP_CHECK_SERVICES:
            method = HTTP_CHECK_SERVICES[name]
            try:
                if method():
                    SERVICE_HEALTH.labels(service=name).set(1)
                    logger.info("HTTP check %s: healthy", name)
                else:
                    SERVICE_HEALTH.labels(service=name).set(0)
                    logger.warning("HTTP check %s: unhealthy", name)
            except Exception as e:
                SERVICE_HEALTH.labels(service=name).set(0)
                logger.error("HTTP check %s failed: %s", name, e)
            continue
        try:
            health = container.attrs.get("State", {}).get("Health", {})
            status = health.get("Status", "unknown")
            logger.info("Container %s health status: %s", name, status)
            if status == "healthy":
                SERVICE_HEALTH.labels(service=name).set(1)
            else:
                SERVICE_HEALTH.labels(service=name).set(0)
        except Exception as e:
            # If Docker API fails, mark unhealthy
            SERVICE_HEALTH.labels(service=name).set(0)
            logger.error(f"Error reading {name}: {e}")


if __name__ == "__main__":
    # Start Prometheus HTTP server
    start_http_server(9100)  # scrape at http://<host>:9100/metrics
    logger.info("Docker API exporter running on port 9100...")

    while True:
        update_metrics()
        time.sleep(SCRAPE_INTERVAL)
