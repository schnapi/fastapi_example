import os
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource

# Tracing
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# Instrumentation
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

from prometheus_client import make_asgi_app


def init_metrics(app):
    # Exposes Prometheus metrics at /metrics
    app.mount("/metrics", make_asgi_app())


def init_tracing(app):
    resource = Resource(
        attributes={
            "service.name": os.getenv("OTEL_SERVICE_NAME", "api"),
            "service.version": "1.0.0",
            "deployment.environment": os.getenv("ENV", "dev"),
        }
    )

    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # Send OTLP/HTTP traces to the collector (e.g., OpenObserve / Otel Collector)
    traces_endpoint = os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT")
    if not traces_endpoint:
        otlp_endpoint = os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4318"
        ).rstrip("/")
        traces_endpoint = f"{otlp_endpoint}/v1/traces"

    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=traces_endpoint))
    )

    return trace.get_tracer(__name__)


def init_metrics_and_tracing(app):
    init_metrics(app)
    init_tracing(app)

    # Instrument FastAPI & HTTPX client
    FastAPIInstrumentor.instrument_app(app)
    HTTPXClientInstrumentor().instrument()
