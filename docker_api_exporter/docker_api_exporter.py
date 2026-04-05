from prometheus_client import start_http_server, Gauge
import docker
import time

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
SCRAPE_INTERVAL = 15  # seconds


def update_metrics():
    containers = client.containers.list(all=True)
    for container in containers:
        name = container.name
        try:
            health = container.attrs.get("State", {}).get("Health", {})
            status = health.get("Status", "unknown")
            if status == "healthy":
                SERVICE_HEALTH.labels(service=name).set(1)
            else:
                SERVICE_HEALTH.labels(service=name).set(0)
        except Exception as e:
            # If Docker API fails, mark unhealthy
            SERVICE_HEALTH.labels(service=name).set(0)
            print(f"Error reading {name}: {e}")


if __name__ == "__main__":
    # Start Prometheus HTTP server
    start_http_server(9100)  # scrape at http://<host>:9100/metrics
    print("Docker API exporter running on port 9100...")

    while True:
        update_metrics()
        time.sleep(SCRAPE_INTERVAL)
