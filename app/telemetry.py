import os
import logging

# Read connection string from environment (set in Container Apps)
APPINSIGHTS_CONNECTION_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "")

logger = logging.getLogger("telemetry")

# Set up Azure Monitor exporter if connection string is available
if APPINSIGHTS_CONNECTION_STRING:
    try:
        from opencensus.ext.azure.log_exporter import AzureLogHandler
        handler = AzureLogHandler(connection_string=APPINSIGHTS_CONNECTION_STRING)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        print("Azure Application Insights telemetry enabled.")
    except Exception as e:
        print(f"Failed to set up Application Insights: {e}")
else:
    logging.basicConfig(level=logging.INFO)
    print("APPLICATIONINSIGHTS_CONNECTION_STRING not set — telemetry disabled (local mode).")


def track_request(prompt_length: int, output_length: int, latency_ms: float):
    """Record inference metrics for a single request."""
    logger.info(
        "inference_request",
        extra={
            "custom_dimensions": {
                "prompt_length": prompt_length,
                "output_length": output_length,
                "latency_ms": round(latency_ms, 2),
            }
        },
    )