import os
from opencensus.ext.azure import metrics_exporter
from opencensus.stats import aggregation, measure, stats, view

# Read connection string from environment (set in Container Apps)
APPINSIGHTS_CONNECTION_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "")

# Define custom measures
m_latency = measure.MeasureFloat("inference/latency", "Inference latency in ms", "ms")
m_prompt_len = measure.MeasureInt("inference/prompt_length", "Prompt length in chars", "chars")
m_output_len = measure.MeasureInt("inference/output_length", "Output length in chars", "chars")

# Register views (aggregations sent to Azure Monitor)
latency_view = view.View(
    "inference_latency_distribution",
    "Distribution of inference latency",
    [],
    m_latency,
    aggregation.DistributionAggregation([50, 100, 200, 500, 1000, 2000]),
)

stats_recorder = stats.Stats()
view_manager = stats_recorder.view_manager
view_manager.register_view(latency_view)

# Set up Azure Monitor exporter if connection string is available
if APPINSIGHTS_CONNECTION_STRING:
    exporter = metrics_exporter.new_metrics_exporter(
        connection_string=APPINSIGHTS_CONNECTION_STRING
    )
    view_manager.register_exporter(exporter)
    print("Azure Application Insights telemetry enabled.")
else:
    print("APPLICATIONINSIGHTS_CONNECTION_STRING not set — telemetry disabled (local mode).")


def track_request(prompt_length: int, output_length: int, latency_ms: float):
    """Record inference metrics for a single request."""
    mmap = stats_recorder.new_measurement_map()
    tmap = stats_recorder.new_tag_map()

    mmap.measure_float_put(m_latency, latency_ms)
    mmap.measure_int_put(m_prompt_len, prompt_length)
    mmap.measure_int_put(m_output_len, output_length)
    mmap.record(tmap)
