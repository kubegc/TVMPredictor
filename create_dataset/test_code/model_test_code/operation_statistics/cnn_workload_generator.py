import numpy as np
import tvm
from tvm import relay
import tvm.relay.testing
from tvm.contrib import graph_executor

def get_network(name, input_shape,dtype="float32"):
    """Get the symbol definition and random weight of a network"""

    layout="NCHW"

    image_shape = input_shape[1:]
    batch_size = input_shape[0]
    output_shape = (batch_size, 1000)
    mod=None

    if name.startswith("resnet-"):
        n_layer = int(name.split("-")[1])
        mod, params = relay.testing.resnet.get_workload(
            num_layers=n_layer,
            batch_size=batch_size,
            layout=layout,
            dtype=dtype,
            image_shape=image_shape,
        )
    elif name.startswith("resnet3d-"):
        n_layer = int(name.split("-")[1])
        mod, params = relay.testing.resnet.get_workload(
            num_layers=n_layer,
            batch_size=batch_size,
            layout=layout,
            dtype=dtype,
            image_shape=image_shape,
        )
    elif name == "mobilenet":
        mod, params = relay.testing.mobilenet.get_workload(
            batch_size=batch_size, layout=layout, dtype=dtype, image_shape=image_shape
        )
    elif name == "squeezenet_v1.1":
        assert layout == "NCHW", "squeezenet_v1.1 only supports NCHW layout"
        mod, params = relay.testing.squeezenet.get_workload(
            version="1.1",
            batch_size=batch_size,
            dtype=dtype,
            image_shape=image_shape,
        )
    elif name == "inception_v3":
        # input_shape = (batch_size, 3, 299, 299) if layout == "NCHW" else (batch_size, 299, 299, 3)
        mod, params = relay.testing.inception_v3.get_workload(batch_size=batch_size, dtype=dtype)
    # elif name == "mxnet":
    #     # an example for mxnet model
    #     from mxnet.gluon.model_zoo.vision import get_model

    #     assert layout == "NCHW"

    #     block = get_model("resnet18_v1", pretrained=True)
    #     mod, params = relay.frontend.from_mxnet(block, shape={"data": input_shape}, dtype=dtype)
    #     net = mod["main"]
    #     net = relay.Function(
    #         net.params, relay.nn.softmax(net.body), None, net.type_params, net.attrs
    #     )
    #     mod = tvm.IRModule.from_expr(net)

    return mod, params, input_shape, output_shape

def compile_without_log(mod, target, params):
    with tvm.transform.PassContext(opt_level=1):
        lib = relay.build(mod, target=target, params=params)
        print()
    return lib

def create_graph_executor_on_single_device(lib,input_shape,target,dtype="float32"):
    dev = tvm.device(str(target), 0)
    module = graph_executor.GraphModule(lib["default"](dev))
    # data_tvm = tvm.nd.array((np.random.uniform(size=input_shape)).astype(dtype))
    # module.set_input("data", data_tvm)
    return module

def evaluate_time_with_tvm_evaluator(module, target):
    # Evaluate
    dev = tvm.device(str(target), 0)
    print("Evaluate inference time cost...")
    ftimer = module.module.time_evaluator("run", dev, repeat=3, min_repeat_ms=500, number=1)
    prof_res = np.array(ftimer().results) * 1e3  # convert to millisecond
    print("Mean inference time (std dev): %.2f ms (%.2f ms)" % (np.mean(prof_res), np.std(prof_res)))