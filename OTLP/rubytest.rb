require 'opentelemetry-sdk'
require 'opentelemetry-exporter-otlp'
require 'opentelemetry-instrumentation-all'

# OpenTelemetry Logger'ı yapılandırma
OpenTelemetry.logger = Logger.new(STDOUT)
OpenTelemetry.logger.level = Logger::DEBUG

# TracerProvider'ı manuel olarak yapılandırma
exporter = OpenTelemetry::Exporter::OTLP::Exporter.new(
  endpoint: 'https://xxxxxxxxxxxxxxxxxxxxxx/api/v2/otlp/v1/traces',
  headers: { 'Authorization' => 'Api-Token dt0c01.xxxxxxxxxxxxxxxxxxxxxxxx' }
)

span_processor = OpenTelemetry::SDK::Trace::Export::SimpleSpanProcessor.new(exporter)

# TracerProvider'ı ayarla
tracer_provider = OpenTelemetry::SDK::Trace::TracerProvider.new
tracer_provider.add_span_processor(span_processor)

# TracerProvider'ı kullan
OpenTelemetry.tracer_provider = tracer_provider
tracer = OpenTelemetry.tracer_provider.tracer('my-tracer')

# Trace oluştur ve gönder
begin
  span = tracer.start_span('Call to /myendpoint', kind: :internal)

  OpenTelemetry::Trace.with_span(span) do |span, context|
    span.set_attribute('http.method', 'GET')
    span.set_attribute('http.url', 'https://xxxxxxxxxxxxxxxxxxx/api/v2/otlp/v1/traces')
    span.set_attribute('net.protocol.version', '1.1')

    puts 'Simulated business logic execution...'
  end
rescue Exception => e
  span&.record_exception(e)
  span&.status = OpenTelemetry::Trace::Status.error("Unhandled exception of type: #{e.class}")
  raise e
ensure
  span&.finish
end

