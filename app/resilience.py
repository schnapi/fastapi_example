from pyresilience import ResilienceRegistry
from pyresilience.observability.prometheus import PrometheusListener
from pyresilience import Resilience, CircuitBreakerConfig, RetryConfig

# Initialize resilience registry
_registry = ResilienceRegistry()
_prom_listener = PrometheusListener()
_registry.add_listener(_prom_listener)

# Circuit breaker config: open after 3 failures, 10s recovery
circuit_breaker_config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout=10.0)
# Retry config: 3 attempts, 2s wait
retry_config = RetryConfig(max_attempts=3, wait_interval=2.0, retry_exceptions=(Exception,))
# Resilience object
resilience = Resilience(circuit_breaker=circuit_breaker_config, retry=retry_config)
