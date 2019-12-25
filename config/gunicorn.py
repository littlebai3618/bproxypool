loglevel = 'debug'
bind = '127.0.0.1:4999'
pidfile = './log/gunicorn.pid'
workers = 2
worker_connections = 2000
x_forwarded_for_header = 'X-FORWARDED-FOR'

accesslog = "./log/api.log"      #访问日志文件
errorlog = "./log/api.log"        #错误日志文件