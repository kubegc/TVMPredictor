from multiprocessing.context import Process
import os
import json
import ast
from TVMProfiler.model_src.analyze_componnet import get_op_info
import tvm
import traceback
import multiprocessing
from multiprocessing import Lock, Pool
class SaveInfo:
    fold_path="Datasets/TVM/models_component/"
    config_name = "dataset.json"
    auto_skip = True

class ModelsRuntimeInfo:
    prefix_fold = "Datasets/"
    fold_path="TVM/datasets_models/"
    config_name = "dataset_auto.json"

def call_back(component_dict):
    return component_dict

def error_call_back(obj):
    print("---error: ",str(obj))
    traceback.print_exc()
    return {"error",str(obj)}

def add_model_component(model_name,shape,batch_size,component_dict,dataset_name="dataset.json",prefix_dataset_name="",fold_path="",auto_skip=True)->dict:
    dataset_name = prefix_dataset_name + dataset_name

    if not os.path.exists(fold_path):
        os.makedirs(fold_path)
    dataset_path = os.path.join(fold_path,dataset_name)

    datasets={}
    if os.path.exists(dataset_path):
        with open(dataset_path,'r') as f:
            datasets = json.load(f)
    
    if model_name.lower() not in datasets.keys():
        datasets[model_name.lower()]={}

    if str(shape) not in datasets[model_name.lower()].keys():
        datasets[model_name.lower()][str(shape)]={}

    if str(batch_size) not in datasets[model_name.lower()][str(shape)].keys() or auto_skip is False:
        datasets[model_name.lower()][str(shape)][str(batch_size)]=component_dict

    with open(dataset_path,"w") as f:
        json.dump(datasets,fp=f,indent=4,separators=(',', ': '),sort_keys=True)

    return datasets

def exist_in_dataset(model_name,shape,batch_size,dataset_name="dataset.json",prefix_dataset_name="",fold_path="")->bool:
    dataset_name = prefix_dataset_name+dataset_name
    if not os.path.exists(fold_path):
        return False
    dataset_path = os.path.join(fold_path,dataset_name)

    datasets={}
    if os.path.exists(dataset_path):
        with open(dataset_path,'r') as f:
            datasets = json.load(f)
    else:
        return False

    if model_name.lower() not in datasets.keys():
        return False

    if str(shape) not in datasets[model_name.lower()].keys():
        return False

    if str(batch_size) not in datasets[model_name.lower()][str(shape)].keys():
        return False

    return True

def init_lock(lk):
    global lock
    lock = lk

def analyze_models_by_runtime_json(deal_function,object_names=[],prefix_dataset_name="",print_info=True):
    lock = multiprocessing.Lock()

    runtime_config = {}
    runtime_config_json_path= os.path.join(ModelsRuntimeInfo.prefix_fold,ModelsRuntimeInfo.fold_path,ModelsRuntimeInfo.config_name)
    if not os.path.exists(runtime_config_json_path):
        print(runtime_config_json_path +" is not found.")
        return False

    with open(runtime_config_json_path,"r") as f:
        runtime_config = json.load(f)

    # ??????models-runtime????????????json??????
    for device_name in runtime_config.keys():
        if device_name=="count":
            continue
        
        for object_name in runtime_config[device_name].keys():
            if object_name=="count":
                continue

            if len(object_names)>0:
                if object_name not in object_names:
                    continue

            for device_id in runtime_config[device_name][object_name].keys():
                if device_id=="count":
                    continue

                for shapes_dimensionality in runtime_config[device_name][object_name][device_id].keys():
                    if shapes_dimensionality=="count":
                        continue
                    
                    pool = Pool(processes=multiprocessing.cpu_count(),initializer=init_lock, initargs=(lock,))
                    for shape in runtime_config[device_name][object_name][device_id][shapes_dimensionality].keys():
                        if shape=="count":
                            continue
                        pool.apply_async(func=run_single_shape,args=(runtime_config,prefix_dataset_name,device_name,object_name,device_id,shapes_dimensionality,shape,True,),error_callback=error_call_back)
                    pool.close()
                    pool.join()
    return True

def run_single_shape_async(runtime_config,prefix_dataset_name,device_name,object_name,device_id,shapes_dimensionality,shape,lock,print_info=True,process_count=1):
    if print_info:
        print("\n")
        print("original device name",device_name)
        print("original device id",device_id)
        print("object name: ",object_name)
        print("shape", shape)

    run_values=[]
    pool = Pool(processes=process_count)

    value = runtime_config[device_name][object_name][device_id][shapes_dimensionality][shape]
    with open(os.path.join(ModelsRuntimeInfo.prefix_fold, value["file_path"]),"r") as f:
        line = f.readline()
        while line is not None and len(line)>0 :
            batch_size = int(line.split(",")[0])

            dshapes = ast.literal_eval(shape.replace("-1",str(batch_size)))

            if not exist_in_dataset(model_name=object_name,shape=shape,batch_size=batch_size,dataset_name=SaveInfo.config_name,fold_path=SaveInfo.fold_path,prefix_dataset_name=prefix_dataset_name):
                run_process=pool.apply_async(func=analyze_model_component,args=(object_name,dshapes,batch_size,print_info,),callback=call_back,error_callback=error_call_back)
                run_values.append((batch_size,run_process))                                   
            line = f.readline()

    pool.close()        # ??????????????????????????????
    pool.join()         # ?????????close/terminate??????????????????????????????????????????

    if print_info:
        print("finish calculate all batch size for shape=%s."%shape)

    with lock: 
        for value in run_values:
            add_model_component(model_name=object_name,shape=shape,batch_size=value[0],component_dict=value[1].get(),prefix_dataset_name=prefix_dataset_name,dataset_name=SaveInfo.config_name,fold_path=SaveInfo.fold_path,auto_skip=SaveInfo.auto_skip)

    if print_info:    
        print("finish record for shape=%s."%shape)

def run_single_shape(runtime_config,prefix_dataset_name,device_name,object_name,device_id,shapes_dimensionality,shape,lock,print_info=True):
    if print_info:
        print("\n")
        print("original device name",device_name)
        print("original device id",device_id)
        print("object name: ",object_name)
        print("shape", shape)

    run_values=[]

    value = runtime_config[device_name][object_name][device_id][shapes_dimensionality][shape]
    with open(os.path.join(ModelsRuntimeInfo.prefix_fold, value["file_path"]),"r") as f:
        line = f.readline()
        while line is not None and len(line)>0 :
            batch_size = int(line.split(",")[0])

            dshapes = ast.literal_eval(shape.replace("-1",str(batch_size)))

            if not exist_in_dataset(model_name=object_name,shape=shape,batch_size=batch_size,dataset_name=SaveInfo.config_name,fold_path=SaveInfo.fold_path,prefix_dataset_name=prefix_dataset_name):
                run_values.append((batch_size,analyze_model_component(object_name,dshapes,batch_size,print_info)))                                   
            line = f.readline()

    if print_info:
        print("finish calculate all batch size for shape=%s."%shape)

    with lock: 
        for value in run_values:
            add_model_component(model_name=object_name,shape=shape,batch_size=value[0],component_dict=value[1],prefix_dataset_name=prefix_dataset_name,dataset_name=SaveInfo.config_name,fold_path=SaveInfo.fold_path,auto_skip=SaveInfo.auto_skip)

    if print_info:    
        print("finish record for shape=%s."%shape)

# ?????????
def analyze_model_component(model_name,dshape,batch_size,print_info=True,dtype="float32"):
    try:
        print("arrange batch_size=%d to process: PID=%d"%(batch_size,os.getpid()))
        device = tvm.cpu(0)
        target = "llvm"
        # device = tvm.cuda(0)
        # target = "cuda"
        print("start to work.")
        component_dict = get_op_info(model_name,dshape[0],device=device,target=target)
        if print_info:
            print("finish analyze for batch_size=%d."%(batch_size))
        return component_dict
    except Exception as ex:
        print("some error happen when deal with batch_size=%d"%batch_size)
        # traceback.print_exc()
        return {"error",str(ex)}

def main():
    print("<%d cores in your device.>"%multiprocessing.cpu_count())
    if analyze_models_by_runtime_json(analyze_model_component,object_names=["mobilenet","resnet-50","resnet3d-50","squeezenet_v1.1"],print_info=True):
        print("finish all works.")
    else:
        print("break off...")

if __name__ == "__main__":
    try:
        main()
    except:
        traceback.print_exc()