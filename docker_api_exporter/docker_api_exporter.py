import logging
import time
import requests
import logging_config
from prometheus_client import start_http_server, Gauge
import tempo_healthcheck
import yaml
# import docker


class ComposeParser:
    def __init__(self, compose_path: str):
        self.compose_path = compose_path
        with open(self.compose_path, "r") as f:
            self.data = yaml.safe_load(f)

    def get_services(self):
        return self.data.get("services", {}) if self.data else {}

    def extract_healthcheck_ports(self):
        result = {}
        for name, config in self.get_services().items():
            ports = config.get("ports", [])
            healthcheck = config.get("healthcheck", None)
            result[name] = {"ports": ports, "healthcheck": healthcheck}
        return result


logging_config.setup_logging(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metric
# 1 = healthy, 0 = unhealthy
SERVICE_HEALTH = Gauge("service_health", "1 if service is healthy, 0 if unhealthy", ["service"])
# Connect to Docker daemon
# client = docker.from_env()
# Scrape loop
SCRAPE_INTERVAL = 3  # seconds


def grafana_healthcheck(service_name, port):
    try:
        response = requests.get(f"http://{service_name}:{port}/api/health", timeout=5)
        return response.status_code == 200 and response.json().get("database") == "ok"
    except Exception as e:
        logger.error(f"Grafana health check failed: {e}")
        return False


def promtail_healthcheck(service_name, port):
    try:
        response = requests.get(f"http://{service_name}:{port}/ready", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Promtail health check failed: {e}")
        return False


def loki_healthcheck(service_name, port):
    try:
        response = requests.get(f"http://{service_name}:{port}/ready", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Loki health check failed: {e}")
        return False


def prometheus_healthcheck(service_name, port):
    try:
        response = requests.get(f"http://{service_name}:{port}/-/ready", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Prometheus health check failed: {e}")
        return False


def mailhog_healthcheck(service_name, port):
    try:
        response = requests.get(f"http://{service_name}:{port}/api/v2/messages", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Mailhog health check failed: {e}")
        return False


def nginx_exporter_healthcheck(service_name, port):
    try:
        response = requests.get(f"http://{service_name}:{port}/metrics", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Nginx exporter health check failed: {e}")
        return False


def vector_healthcheck(service_name, port):
    return True
    try:
        response = requests.get(f"http://{service_name}:{port}/metrics", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Vector health check failed: {e}")
        return False


# list of services where health is determined via HTTP
HTTP_CHECK_SERVICES = {
    "tempo": tempo_healthcheck.check_tempo_comprehensive,
    "docker-api-exporter": lambda service_name, port: True,
    "grafana": grafana_healthcheck,
    # "promtail": promtail_healthcheck,
    "vector": vector_healthcheck,
    "loki": lambda service_name, port: True,
    "prometheus": prometheus_healthcheck,
    "mailhog": mailhog_healthcheck,
    "nginx_exporter": nginx_exporter_healthcheck,
    "nginx": lambda service_name, port: True,
    "nginx-exporter": lambda service_name, port: True,
    "api": lambda service_name, port: True,
    "frontend": lambda service_name, port: True,
}


def update_metrics():
    # containers = client.containers.list(all=True)
    parser = ComposeParser("docker-compose.yml")
    for container_name, container in parser.extract_healthcheck_ports().items():
        # First, check if this service needs HTTP healthcheck
        if container_name in HTTP_CHECK_SERVICES:
            method = HTTP_CHECK_SERVICES[container_name]
            try:
                port = (
                    container["ports"][0].split(":")[-1]
                    if isinstance(container["ports"], list) and container["ports"]
                    else ""
                )
                if method(container_name, port):
                    SERVICE_HEALTH.labels(service=container_name).set(1)
                    logger.info(f"HTTP check {container_name}: healthy")
                else:
                    SERVICE_HEALTH.labels(service=container_name).set(0)
                    logger.warning(f"HTTP check {container_name}: unhealthy")
            except Exception as e:
                SERVICE_HEALTH.labels(service=container_name).set(0)
                logger.exception(f"HTTP check {container_name} failed: {e}")
            continue
        logger.warning(f"No HTTP check defined for {container_name}")


if __name__ == "__main__":
    # Start Prometheus HTTP server
    start_http_server(9100)  # scrape at http://<host>:9100/metrics
    logger.info("Docker API exporter running on port 9100...")

    while True:
        time.sleep(3)  # initial delay to allow services to start
        update_metrics()
        time.sleep(SCRAPE_INTERVAL)
