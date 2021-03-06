from create_dataset.common import generate_datasets_with_one_dimensionality_changing,uniform_sampling,generate_dataset_with_one_dimensionality_changing
import tvm.relay as relay
import create_dataset.test_code.op_test_code.config.common_args as common_args

import os
from optparse import OptionParser
parser = OptionParser(usage="define device name")
parser.add_option("-c", "--cpu_num", action="store",
                  dest="cpu_num",
                  default=False,
                  type="int",
                  help="cpu number")
(options, args) = parser.parse_args()
cpu_num = options.cpu_num
os.environ["TVM_NUM_THREADS"] = str(cpu_num)

common_args.fold_path = "TVM/datasets_huyi/" + str(cpu_num) +"/"


def calculate_op(dshape,dtype="float32"):
    data = relay.var("input_x", shape=dshape[0], dtype=dtype)
    weight = relay.var("weight", shape=dshape[1], dtype=dtype)
    f = relay.nn.conv2d(data=data,weight=weight,channels=32, kernel_size=(3, 3), strides=(2, 2),padding=(1, 1))

    return f

# 定义参数
function_dict = {"func":calculate_op, "name": "nn.conv2d"}

# 限定shape
count = 7
force_shape_relation=(None,None)
shapes_dimensionality=((4,4),(0,0))

# shape_ = ((28,28),(32,32),(64,64),(128,128),(156,156),(224,224),(256,256))
# for i in range(7):
#     range_min = ((-1,3,*shape_[i]),(32,3,3,3))
#     range_max = ((-1,3,*shape_[i]),(32,3,3,3))
#     generate_datasets_with_one_dimensionality_changing(device_parame_array=common_args.device_parame_array,count=i+1,shape_dimensionality=shapes_dimensionality,range_min=range_min,range_max=range_max,function_dict = function_dict,min_shapes=common_args.min_shapes,max_shapes=common_args.max_shapes,sampling=common_args.sampling,force_shape_relation=force_shape_relation,dtype=common_args.dtype,cycle_times=common_args.cycle_times,min_repeat_ms=common_args.min_repeat_ms,opt_level=common_args.opt_level,prefix_path=common_args.prefix_path,fold_path=common_args.fold_path,device_name=common_args.device_name,show_print=common_args.show_print)

count = 1
range_min = [[-1,3,1,1],[32,3,3,3]]
range_max = [[-1,3,100,100],[32,3,3,3]]
for a in uniform_sampling(10,100,0.1):
    for b in uniform_sampling(10,100,0.1):
        range_min[0][2]=a
        range_max[0][2]=a
        range_min[0][3]=b
        range_max[0][3]=b

        generate_datasets_with_one_dimensionality_changing(device_parame_array=common_args.device_parame_array,count=count,shape_dimensionality=shapes_dimensionality,range_min=range_min,range_max=range_max,function_dict = function_dict,min_shapes=common_args.min_shapes,max_shapes=common_args.max_shapes,sampling=common_args.sampling,force_shape_relation=force_shape_relation,dtype=common_args.dtype,cycle_times=common_args.cycle_times,min_repeat_ms=common_args.min_repeat_ms,opt_level=common_args.opt_level,prefix_path=common_args.prefix_path,fold_path=common_args.fold_path,device_name=common_args.device_name,show_print=common_args.show_print)
        count+=1


