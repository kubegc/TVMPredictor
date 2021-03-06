import onnx
import tvm
from create_dataset.common import generate_datasets_with_one_dimensionality_changing,Device
from optparse import OptionParser

parser = OptionParser(usage="define device name")
parser.add_option("-d", "--device_name", action="store",
                  dest="device_name",
                  default=False,
                  type="string",
                  help="instance type")
(options, args) = parser.parse_args()

def calculate_lstm(dshape,dtype="float32"):
    '''
    test add-op in one kind of shape.

    Parameters
    ----------

    exp:
    * GPU: target = "cuda", device = tvm.cuda(0)
    * CPU: target = "llvm", device=tvm.cpu(0)
    '''

    onnx_model = onnx.load("create_dataset/test_code/model_test_code/lstm.onnx")
    shape_dict = {'input': (dshape[0][0], dshape[0][1], dshape[0][2]), 'h0':(dshape[1][0], dshape[1][1], dshape[1][2]), 'c0':(dshape[1][0], dshape[1][1], dshape[1][2])}
    mod, params = tvm.relay.frontend.from_onnx(onnx_model, shape_dict)

    return mod

min_shapes=1
max_shapes=201
sampling=1.0
dtype="float32"

isModule=True
cycle_times=3
min_repeat_ms=30
opt_level=0
prefix_path="Datasets/"
fold_path="TVM/datasets_model/"
device_name=options.device_name
show_print=True

count = 1
shapes_dimensionality3=((3,3),(0,1))
device_parame_array = [Device.device_params_GPU0]
force_shape_relation=(None,(None, lambda x,y,z:y, None))

range_min3 = ((5,-1,10),(2,-1,20))
range_max3 = ((5,-1,10),(2,-1,20))
function_dict = {"func":calculate_lstm, "name": "lstm"}
generate_datasets_with_one_dimensionality_changing(device_parame_array=device_parame_array,count=count,shape_dimensionality=shapes_dimensionality3,range_min=range_min3,range_max=range_max3,function_dict = function_dict,min_shapes=min_shapes,max_shapes=max_shapes,sampling=sampling,force_shape_relation=force_shape_relation,dtype=dtype,cycle_times=cycle_times,min_repeat_ms=min_repeat_ms,opt_level=opt_level,prefix_path=prefix_path,fold_path=fold_path,device_name=device_name,show_print=show_print,isModule=isModule,dataset_config_name="dataset_"+device_name+".json")
