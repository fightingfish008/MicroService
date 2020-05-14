config = {'AMQP_URI': "amqp://guest:123456@ip"}
from nameko.standalone.rpc import ClusterRpcProxy
with ClusterRpcProxy(config) as rpc:
    # result = rpc.sender_service.dispatch_method("world")
    # result_async = rpc.sender_service.dispatch_method.call_async("world async")
    result = rpc.admin.login(username="hello", passwd=123456)
    print(result)
    # result_async = rpc.admin.login.call_async(3, 4)
    result = rpc.admin.hello("world")
    # result_async = rpc.greeting_service.hello.call_async("world async")
    print(result)
    pass
    # print(result_async.result())