import os
bind = f"0.0.0.0:{os.getenv('PORT', 5000)}"
workers = 2
worker_class = "sync"
timeout = 30
keepalive = 2
max_requests = 1000
preload_app = True
accesslog = "-"
errorlog = "-"
loglevel = "info"
