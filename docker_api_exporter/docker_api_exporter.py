import logging
import time
import requests
from prometheus_client import start_http_server, Gauge
import docker
import tempo_healthcheck


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metric
# 1 = healthy, 0 = unhealthy
SERVICE_HEALTH = Gauge("service_health", "1 if service is healthy, 0 if unhealthy", ["service"])
# Connect to Docker daemon
client = docker.from_env()
# Scrape loop
SCRAPE_INTERVAL = 60  # seconds


def grafana_healthcheck():
    try:
        response = requests.get("http://grafana:3000/api/health", timeout=5)
        return response.status_code == 200 and response.json().get("database") == "ok"
    except Exception as e:
        logger.error(f"Grafana health check failed: {e}")
        return False


def promtail_healthcheck():
    try:
        response = requests.get("http://promtail:9080/ready", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Promtail health check failed: {e}")
        return False


def loki_healthcheck():
    try:
        response = requests.get("http://loki:3100/ready", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Loki health check failed: {e}")
        return False


def prometheus_healthcheck():
    try:
        response = requests.get("http://prometheus:9090/-/ready", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Prometheus health check failed: {e}")
        return False


def mailhog_healthcheck():
    try:
        response = requests.get("http://mailhog:8025/api/v2/messages", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Mailhog health check failed: {e}")
        return False


def nginx_exporter_healthcheck():
    try:
        response = requests.get("http://nginx-exporter:9113/metrics", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Nginx exporter health check failed: {e}")
        return False


# list of services where health is determined via HTTP
HTTP_CHECK_SERVICES = {
    "tempo": tempo_healthcheck.check_tempo_comprehensive,
    "docker-api-exporter": lambda: True,
    "grafana": grafana_healthcheck,
    "promtail": promtail_healthcheck,
    "loki": loki_healthcheck,
    "prometheus": prometheus_healthcheck,
    "mailhog": mailhog_healthcheck,
    "nginx_exporter": nginx_exporter_healthcheck,
}


def update_metrics():
    containers = client.containers.list(all=True)
    for container in containers:
        name = container.name
        name_norm = "docker-api-exporter" if "docker-api-exporter" in container.name else name

        # First, check if this service needs HTTP healthcheck
        if name_norm in HTTP_CHECK_SERVICES:
            method = HTTP_CHECK_SERVICES[name_norm]
            try:
                if method():
                    SERVICE_HEALTH.labels(service=name).set(1)
                    logger.info(f"HTTP check {name}: healthy")
                else:
                    SERVICE_HEALTH.labels(service=name).set(0)
                    logger.warning(f"HTTP check {name}: unhealthy")
            except Exception as e:
                SERVICE_HEALTH.labels(service=name).set(0)
                logger.error(f"HTTP check {name} failed: {e}")
            continue
        try:
            health = container.attrs.get("State", {}).get("Health", {})
            status = health.get("Status", "unknown")
            logger.info(f"Container {name} health status: {status}")
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
