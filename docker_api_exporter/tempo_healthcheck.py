import requests
import socket
import sys
import logging

logger = logging.getLogger(__name__)


def check_tempo_comprehensive(service_name, port):
    checks = {"metrics_endpoint": False, "otlp_port": False}

    # Check metrics endpoint
    try:
        response = requests.get(f"http://{service_name}:{port}/metrics", timeout=5)
        checks["metrics_endpoint"] = (
            response.status_code == 200 and "go_goroutines" in response.text
        )
    except Exception as e:
        logger.error(f"Metrics check failed: {e}")
        return False

    # Check OTLP port
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(("tempo", 4317))
        sock.close()
        checks["otlp_port"] = result == 0
    except Exception as e:
        logger.error(f"OTLP port check failed: {e}")
        return False

    return all(checks.values())


if __name__ == "__main__":
    is_healthy = check_tempo_comprehensive()
    sys.exit(0 if is_healthy else 1)
