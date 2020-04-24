# nameko run UserService.service --broker amqp://guest:123456@localhost
import importlib
from pathlib import Path

root = Path(__file__).parent


def run_all():
    services = {}
    for f in root.iterdir():
        if f.is_dir() and f.name.endswith("Service"):
            name = f.name
            service = importlib.import_module(name + '.service')
            services[name] = service
    from nameko.runners import ServiceRunner

    runner = ServiceRunner(config={"AMQP_URI": "amqp://guest:123456@47.114.57.220:5672/"})
    for name, service in services.items():
        cls = getattr(service, name)
        print(name,service,cls)
        runner.add_service(cls)

    print('wsadsa')

    runner.start()
    try:
        runner.wait()
    except KeyboardInterrupt:
        runner.kill()
    runner.stop()


if __name__ == '__main__':
    run_all()
