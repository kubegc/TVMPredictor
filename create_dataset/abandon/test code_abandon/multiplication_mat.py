# create the runtime-dataset for add-op

from create_dataset.common import create_dataset_2d, test_op_time,test_data_copy_time
import tvm.relay as relay
import tvm

shape = (100,100,100)

def calculate_time(dshape,dtype="float32",target="llvm", device=tvm.cpu(0)):
    '''
    test add-op in one kind of shape.

    Parameters
    ----------
    * input_dict:   give the real inputs. exp: { var_name_str: (shape,type)}
    * output:   give the real output that is compute by inputs
    * min_value ~ max_value:    when create the random input values, this gives the range.

    exp:
    * GPU: target = "cuda", device = tvm.cuda(0)
    * CPU: target = "llvm", device=tvm.cpu(0)
    '''

    dshape=convert_shape(dshape)
    # print(dshape)

    x = relay.var("input_x", shape=dshape[0], dtype=dtype)
    y = relay.var("input_y", shape=dshape[1], dtype=dtype)
    f = relay.nn.batch_matmul(x,y)

    return test_op_time(input_dict={"input_x": (dshape[0],dtype), "input_y":(dshape[1],dtype)},output=f,cycle_times=25,target=target, device=device)

def convert_shape(shapes):
    if len(shapes[0])<3:
        shapes=[(1,*(shapes[0])), (1,*(shapes[1]))]

    return shapes

def relation(x,y):
    if len(x)!=len(y) or len(x)<2:
        return False

    if x[-1] != y[-1]:
        return False

    for i in range(len(x)):
        if i>= len(x)-2:
            break

        if x[i]!=y[i]:
            return False
    
    return True

def calculate_copy_time(dshape,dtype="float32",target="llvm", device=tvm.cpu(0)):
    '''
    test add-op in one kind of shape.

    Parameters
    ----------
    * input_dict:   give the real inputs. exp: { var_name_str: (shape,type)}
    * output:   give the real output that is compute by inputs
    * min_value ~ max_value:    when create the random input values, this gives the range.

    exp:
    * GPU: target = "cuda", device = tvm.cuda(0)
    * CPU: target = "llvm", device=tvm.cpu(0)
    '''

    dshape=convert_shape(dshape)
    # print(dshape)

    x = relay.var("input_x", shape=dshape[0], dtype=dtype)
    y = relay.var("input_y", shape=dshape[1], dtype=dtype)
    f = relay.nn.batch_matmul(x,y)

    return test_data_copy_time(input_dict={"input_x": (dshape[0],dtype), "input_y":(dshape[1],dtype)},output=f,cycle_times=25,target=target, device=device)

# create_dataset_2d(function={"body":calculate_time,"params":{"target": "llvm", "device": tvm.cpu(0)}},max_shapes=((100,100,100),(100,100,100)),sampling=((0.1,0.1,0.1),(0.1,0.1,0.1)),dtype="float32",file_name="mul_mat_float.txt",limit=relation,fold_path="create_dataset/datasets/dell04/")
# create_dataset_2d(function={"body":calculate_time,"params":{"target": "cuda", "device": tvm.cuda(0)}},max_shapes=((100,100,100),(100,100,100)),sampling=((0.1,0.1,0.1),(0.1,0.1,0.1)),dtype="float32",file_name="mul_mat_float_gpu.txt",limit=relation,fold_path="create_dataset/datasets/dell04/")

create_dataset_2d(function={"body":calculate_copy_time,"params":{"target": "llvm", "device": tvm.cpu(0)}},max_shapes=((100,100,100),(100,100,100)),sampling=((0.1,0.1,0.1),(0.1,0.1,0.1)),dtype="float32",file_name="copy_mul_mat_float.txt",limit=relation,fold_path="create_dataset/datasets/dell04/")
create_dataset_2d(function={"body":calculate_copy_time,"params":{"target": "cuda", "device": tvm.cuda(0)}},max_shapes=((100,100,100),(100,100,100)),sampling=((0.1,0.1,0.1),(0.1,0.1,0.1)),dtype="float32",file_name="copy_mul_mat_float_gpu.txt",limit=relation,fold_path="create_dataset/datasets/dell04/")