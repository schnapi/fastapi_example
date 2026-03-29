import time
import httpx
from prometheus_client import Counter, Histogram
from fastapi import Request

# Metrics for outgoing calls
OUTGOING_HTTP_REQUESTS = Counter(
    "http_requests_total", "Total outgoing HTTP requests", ["method", "endpoint", "status_code"]
)
OUTGOING_HTTP_LATENCY = Histogram(
    "http_request_latency_seconds", "Latency of outgoing HTTP requests", ["method", "endpoint"]
)
# Incoming traffic metrics
INCOMING_REQUESTS = Counter(
    "incoming_requests_total", "Total incoming HTTP requests", ["method", "endpoint", "status_code"]
)
INCOMING_LATENCY = Histogram(
    "incoming_request_latency_seconds", "Latency of incoming HTTP requests", ["method", "endpoint"]
)


# Wrapper for outgoing HTTP requests
async def tracked_request(method, url, **kwargs):
    start = time.time()
    async with httpx.AsyncClient() as client:
        response = await client.request(method, url, **kwargs)
    elapsed = time.time() - start

    OUTGOING_HTTP_REQUESTS.labels(
        method=method, endpoint=url, status_code=response.status_code
    ).inc()
    OUTGOING_HTTP_LATENCY.labels(method=method, endpoint=url).observe(elapsed)

    return response


# Middleware function (not yet attached to app)
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start

    endpoint = request.url.path
    INCOMING_REQUESTS.labels(
        method=request.method, endpoint=endpoint, status_code=response.status_code
    ).inc()
    INCOMING_LATENCY.labels(method=request.method, endpoint=endpoint).observe(elapsed)

    return response
