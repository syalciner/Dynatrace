require 'net/http'
require 'json'
require 'sys/proctable'
include Sys

# Dynatrace Metrics Ingest API Endpoint ve API Token
METRIC_ENDPOINT = 'https://xxxxxxxxx/api/v2/metrics/ingest'
API_TOKEN = 'dt0c01.xxxxxxxxxxxxxxxxxxxxxxxx'

# Metric Gönderim Fonksiyonu
def send_metric(cpu_usage)
  uri = URI(METRIC_ENDPOINT)
  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = true

  headers = {
    'Authorization' => "Api-Token #{API_TOKEN}",
    'Content-Type' => 'text/plain; charset=utf-8'
  }

  # Dynatrace Plain Text Metric Format
  metric_data = "system.cpu.usage,environment=production #{cpu_usage} #{(Time.now.to_f * 1000).to_i}"

  request = Net::HTTP::Post.new(uri, headers)
  request.body = metric_data

  response = http.request(request)

  if response.code == '202'
    puts "Metric sent successfully: #{metric_data}"
  else
    puts "Failed to send metric: #{response.code} - #{response.body}"
  end
end

# CPU Kullanımını Hesaplama Fonksiyonu
def calculate_cpu_usage
  proc_info = ProcTable.ps.first
  if proc_info
    cpu_percentage = ((proc_info.utime + proc_info.stime).to_f / proc_info.rss.to_f) * 100 rescue 0
    cpu_percentage.round(2)
  else
    0
  end
end

# Sürekli Gönderim Döngüsü
loop do
  cpu_usage = calculate_cpu_usage
  puts "Current CPU Usage: #{cpu_usage}%"
  send_metric(cpu_usage)
  sleep 5 # Her 5 saniyede bir gönderim
end
