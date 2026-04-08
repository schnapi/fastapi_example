import time
import logging
import uuid
from fastapi import Request
import httpx
from prometheus_client import Counter, Histogram
from app.utils.geoip_utils import get_country_from_ip, extract_client_ip

logger = logging.getLogger("metrics")

# Outgoing requests
OUTGOING_HTTP_REQUESTS = Counter(
    "http_requests_total", "Total outgoing HTTP requests", ["method", "endpoint", "status_code"]
)
OUTGOING_HTTP_LATENCY = Histogram(
    "http_request_latency_seconds", "Latency of outgoing HTTP requests", ["method", "endpoint"]
)
# Incoming requests
INCOMING_REQUESTS = Counter(
    "incoming_requests_total", "Total incoming HTTP requests", ["method", "endpoint", "status_code"]
)
INCOMING_LATENCY = Histogram(
    "incoming_request_latency_seconds", "Latency of incoming HTTP requests", ["method", "endpoint"]
)


class TrackedAsyncClient(httpx.AsyncClient):
    async def request(self, method, url, **kwargs):
        start = time.time()
        logger.info(f"Outgoing request: {method} {url}")
        try:
            response = await super().request(method, url, **kwargs)
            elapsed = time.time() - start
            status_code = response.status_code
            OUTGOING_HTTP_REQUESTS.labels(
                method=method, endpoint=url, status_code=status_code
            ).inc()
            OUTGOING_HTTP_LATENCY.labels(method=method, endpoint=url).observe(elapsed)

            logger.info(
                f"Outgoing response: {method} {url} status={status_code} duration={elapsed:.3f}s"
            )

            if status_code >= 500 or elapsed > 2.0:
                logger.warning(
                    "Slow external call",
                    extra={
                        "method": method,
                        "endpoint": url,
                        "status_code": status_code,
                        "duration": round(elapsed, 3),
                    },
                )
            return response

        except Exception:
            elapsed = time.time() - start
            logger.error(
                "External request failed",
                extra={"method": method, "endpoint": url, "duration": round(elapsed, 3)},
                exc_info=True,
            )
            OUTGOING_HTTP_REQUESTS.labels(method=method, endpoint=url, status_code="error").inc()
            raise


# Middleware function (not yet attached to app)
async def metrics_middleware(request: Request, call_next):
    method = request.method
    endpoint = request.url.path
    client_ip = extract_client_ip(request)
    country = get_country_from_ip(client_ip)

    # Generate request ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    request.state.client_ip = client_ip
    request.state.country = country

    start = time.time()
    is_log_info = logger.isEnabledFor(logging.INFO)
    if is_log_info:
        logger.info(f"Incoming request: {method} {endpoint} from {client_ip} ({country})")
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(
            "Unhandled request error",
            extra={
                "request_id": request_id,
                "method": method,
                "endpoint": endpoint,
                "client_addr": client_ip,
                "country": country,
            },
            exc_info=True,  # includes full traceback in logs
        )
        raise

    elapsed = time.time() - start
    status_code = response.status_code
    # Metrics
    INCOMING_REQUESTS.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    INCOMING_LATENCY.labels(method=method, endpoint=endpoint).observe(elapsed)
    # Info logs (dev only)
    if is_log_info:
        logger.info(
            f"Completed request: {method} {endpoint} status={status_code} duration={elapsed:.3f}s from {client_ip}"
        )
    # Production logs (important signals)
    if status_code >= 500 or elapsed > 2.0:
        logger.warning(
            "Slow or failing request",
            extra={
                "request_id": request_id,
                "method": method,
                "endpoint": endpoint,
                "status_code": status_code,
                "duration": round(elapsed, 3),
                "client_addr": client_ip,
                "country": country,
            },
        )
    return response
