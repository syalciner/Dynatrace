require 'opentelemetry-sdk'
require 'opentelemetry-exporter-otlp'
require 'opentelemetry-instrumentation-all'
require 'net/http'

# Logger yapılandırması
OpenTelemetry.logger = Logger.new(STDOUT)
OpenTelemetry.logger.level = Logger::DEBUG

# Kaynak tanımı
resource_attributes = {
  'service.name' => 'ruby-agent',
  'service.version' => '0.1.0'
}
resource = OpenTelemetry::SDK::Resources::Resource.create(resource_attributes)

# === TRACE ===
# Trace Provider ve Exporter yapılandırması
trace_exporter = OpenTelemetry::Exporter::OTLP::Exporter.new(
  endpoint: 'https://xxxxxx/api/v2/otlp/v1/traces',
  headers: { 'Authorization' => 'Api-Token dt0c01.xxxxxxxxxxxxxxxxxxxxxxxxxxxx' }
)
trace_processor = OpenTelemetry::SDK::Trace::Export::BatchSpanProcessor.new(trace_exporter)

trace_provider = OpenTelemetry::SDK::Trace::TracerProvider.new(resource: resource)
trace_provider.add_span_processor(trace_processor)
OpenTelemetry.tracer_provider = trace_provider

# Tracer tanımı
tracer = OpenTelemetry.tracer_provider.tracer('ruby-tracer')

# === METRICS: Metric Gönderim Fonksiyonu ===
def send_metric(endpoint, api_token, metric_data)
  uri = URI(endpoint)
  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = true

  headers = {
    'Authorization' => "Api-Token #{api_token}",
    'Content-Type' => 'text/plain; charset=utf-8'
  }

  request = Net::HTTP::Post.new(uri, headers)
  request.body = metric_data

  response = http.request(request)

  if response.code == '202'
    puts "Metric sent successfully: #{metric_data.strip}"
  else
    puts "Failed to send metric: #{response.code} - #{response.body}"
  end
end

metric_endpoint = 'https://xxxxxxxxxxxxxxxx/api/v2/metrics/ingest'
api_token = 'dt0c01.xxxxxxxxxxxxxxxxxxxxxxxxx'

# === Trace ve Metric gönderimi ===
loop do
  begin
    # TRACE: Parent span
    parent_span = tracer.start_span('Parent Operation', kind: :server)
    OpenTelemetry::Trace.with_span(parent_span) do |span, context|
      parent_span.set_attribute('operation.id', rand(1000))
      parent_span.set_attribute('operation.name', 'parent_process')

      # Child span 1
      child_span_1 = tracer.start_span('Child Operation 1', kind: :client)
      OpenTelemetry::Trace.with_span(child_span_1) do |child_span, _context|
        child_span_1.set_attribute('db.system', 'postgresql')
        child_span_1.set_attribute('db.statement', 'SELECT * FROM users WHERE id = 1')
      ensure
        child_span_1.finish
      end

      # Child span 2
      child_span_2 = tracer.start_span('Child Operation 2', kind: :client)
      OpenTelemetry::Trace.with_span(child_span_2) do |child_span, _context|
        child_span_2.set_attribute('http.method', 'POST')
        child_span_2.set_attribute('http.url', 'https://xxxxxxxxxxxxxxxxxxxxx/api/v2/otlp/v1/traces')
      ensure
        child_span_2.finish
      end
    ensure
      parent_span.finish
    end

    puts 'Trace sent successfully!'

    # METRIC: Custom Metrics
    timestamp = (Time.now.to_f * 1000).to_i
    metric_data = <<~METRIC
      app.requests.total,env=production,service=inventory #{rand(1000..2000)} #{timestamp}
      app.cpu.usage,env=production,service=inventory #{rand(1..100)} #{timestamp}
    METRIC

    send_metric(metric_endpoint, api_token, metric_data)

    # Sleep between iterations
    sleep 5
  rescue StandardError => e
    puts "Error occurred: #{e.message}"
    puts e.backtrace.join("\n")
  end
end
