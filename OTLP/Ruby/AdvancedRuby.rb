require 'opentelemetry-sdk'
require 'opentelemetry-exporter-otlp'
require 'opentelemetry-instrumentation-all'

# OpenTelemetry Logger'ı yapılandırma
OpenTelemetry.logger = Logger.new(STDOUT)
OpenTelemetry.logger.level = Logger::DEBUG

# TracerProvider'ı manuel olarak yapılandırma
exporter = OpenTelemetry::Exporter::OTLP::Exporter.new(
  endpoint: 'https://xxxxxxxxxxxx/api/v2/otlp/v1/traces',
  headers: { 'Authorization' => 'Api-Token dt0c01.Xxxxxxxxxxxxxxxxxx' }
)

span_processor = OpenTelemetry::SDK::Trace::Export::SimpleSpanProcessor.new(exporter)

# TracerProvider'ı ayarla
tracer_provider = OpenTelemetry::SDK::Trace::TracerProvider.new
tracer_provider.add_span_processor(span_processor)

# TracerProvider'ı kullan
OpenTelemetry.tracer_provider = tracer_provider
tracer = OpenTelemetry.tracer_provider.tracer('advanced-tracer')

# Sürekli trace gönderimi için döngü
loop do
  begin
    # Ana işlem için bir span başlat
    parent_span = tracer.start_span('Parent Operation', kind: :server)
    OpenTelemetry::Trace.with_span(parent_span) do |span, context|
      parent_span.set_attribute('operation.id', rand(1000))
      parent_span.set_attribute('operation.name', 'parent_process')
      parent_span.add_event('Parent span started', attributes: { 'timestamp' => Time.now.to_s })

      # Alt işlem 1 (Child span)
      child_span_1 = tracer.start_span('Child Operation 1', kind: :client)
      OpenTelemetry::Trace.with_span(child_span_1) do |span, context|
        child_span_1.set_attribute('db.system', 'postgresql')
        child_span_1.set_attribute('db.statement', 'SELECT * FROM users WHERE id = 1')
        child_span_1.add_event('Database query executed', attributes: { 'query.execution_time' => '50ms' })
      ensure
        child_span_1.finish
      end

      # Alt işlem 2 (Child span)
      child_span_2 = tracer.start_span('Child Operation 2', kind: :client)
      OpenTelemetry::Trace.with_span(child_span_2) do |span, context|
        child_span_2.set_attribute('http.method', 'POST')
        child_span_2.set_attribute('http.url', 'https://api.example.com/process')
        child_span_2.add_event('API call initiated', attributes: { 'api.response_time' => '200ms' })
      ensure
        child_span_2.finish
      end

      parent_span.add_event('Parent span finished', attributes: { 'child_operations' => 2 })
    ensure
      parent_span.finish
    end

    # 5 saniyelik bekleme süresi
    puts 'Trace sent successfully!'
    sleep 5
  rescue Exception => e
    puts "Error occurred: #{e.message}"
  end
end

