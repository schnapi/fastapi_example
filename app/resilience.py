from pyresilience import ResilienceRegistry
from pyresilience.contrib.prometheus import PrometheusListener
from pyresilience import ResilienceConfig, CircuitBreakerConfig, RetryConfig

# Prometheus listener
_prom_listener = PrometheusListener()

# Circuit breaker config: open after 3 failures, 10s recovery
circuit_breaker_config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout=10.0)

# Retry config: 3 attempts, 2s wait
retry_config = RetryConfig(max_attempts=3)

# Resilience configuration
resilience_config = ResilienceConfig(
    circuit_breaker=circuit_breaker_config,
    retry=retry_config,
    listeners=[_prom_listener],  # Add listener here
)

# from pyresilience.contrib.fastapi import ResilientDependency
# resilient_dep = ResilientDependency(resilience_config)

# Initialize resilience registry with config
registry = ResilienceRegistry()
registry.register("default", resilience_config)
