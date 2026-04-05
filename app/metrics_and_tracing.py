import os
from starlette.middleware.wsgi import WSGIMiddleware
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource

# Tracing
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor  # ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.prometheus import PrometheusMetricReader

# Instrumentation
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor


def init_metrics(app):
    # Metrics setup - Prometheus exporter
    reader = PrometheusMetricReader()  # Exposes /metrics
    provider = MeterProvider(metric_readers=[reader])
    metrics.set_meter_provider(provider)
    app.mount("/metrics", WSGIMiddleware(reader))


def init_tracing(app):
    resource = Resource(
        attributes={
            "service.name": "my_fastapi_service",
            "service.version": "1.0.0",
            "deployment.environment": os.getenv("ENV", "dev"),
        }
    )
    # Tracing only
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint="http://tempo:4317", insecure=True))
    )
    return trace.get_tracer(__name__)


def init_metrics_and_tracing(app):
    init_metrics(app)
    init_tracing(app)

    # # Optional: export traces to console (for debugging)
    # tracer = trace.get_tracer(__name__)
    # span_processor = BatchSpanProcessor(ConsoleSpanExporter())
    # trace.get_tracer_provider().add_span_processor(span_processor)

    # Configure logging to stdout (Promtail will read it)
    # level = logging.INFO if os.getenv("ENV") == "dev" else logging.WARNING
    # logging.basicConfig(level=level, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s")

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
    HTTPXClientInstrumentor().instrument()
