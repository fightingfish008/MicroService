# nameko run UserService/service --broker amqp://admin:wxs1995.@139.199.10.230
from pathlib import Path

import sys

root = Path(__file__).absolute().parent.parent
template = '''[program:{}] 
command=nameko run {}Service.service --broker amqp://guest:123456@ip
directory=/app/MicroService             ; 执行 command 之前，先切换到工作目录
user=wxs                                ; 使用 ubuntu 用户来启动该进程
autorestart=true                        ; 自动重启
redirect_stderr=true                    ; 重定向输出的日志
stdout_logfile =/var/log/supervisord/{}.log
loglevel=info
'''
group = '''[group:micro]
programs={}                             ; each refers to 'x' in [program:x] definitions
priority=999                            ; the relative start priority (default 999)
'''


def conf_maker(base='/etc/supervisor'):
    groups = []
    for f in root.iterdir():
        if f.is_dir() and f.name.endswith("Service"):
            service = f.name[:-7]
            config_name = "micro_" + service.lower()
            content = template.format(config_name, service,  config_name)
            write_conf(config_name, content, base)
            groups.append(config_name)
    group_conf = group.format(','.join(groups))
    write_conf('group_micro', group_conf, base)


def write_conf(name, content, base):
    path = '/'.join([base, name + '.conf'])
    with open(path, 'w+') as f:
        f.write(content)
        f.flush()


def test():
    base = str(root.joinpath('conf'))
    print(base)
    conf_maker(base)


if __name__ == '__main__':
    print(root)
    try:
        if sys.argv[1] == '--run':
            conf_maker()
        elif sys.argv[1] == '--test':
            test()
    except Exception as e:
        print(e)
        print("no arg")
