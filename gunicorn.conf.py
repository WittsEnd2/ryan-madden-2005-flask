import os
import multiprocessing

# Server socket
bind = f"{os.environ.get('HOST', '0.0.0.0')}:{os.environ.get('PORT', '5000')}"
backlog = 2048

# Worker processes
workers = int(os.environ.get('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
threads = int(os.environ.get('THREADS', 2))
timeout = int(os.environ.get('TIMEOUT', 120))
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'nfl_game'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
