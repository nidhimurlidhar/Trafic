import os.path
import numpy as np
import json
from fiberfileIO import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--class_data', action='store', dest='class_data', help='JSON file comntaining the classification results', default='')
parser.add_argument('--input', action='store', dest='input_fiber', help='VTK file containing the origin fiber tract used for the classification', default='')
parser.add_argument('--output_dir', action='store', dest='output_dir', help='Output directory', default='')


def reformat_prediction(predictions, num_classes):
    vector_id_blank = []
    for i in range(num_classes):
        vector_id_blank.append(vtk.vtkIdTypeArray())
    dict_pred = {}
    for pred_class, indexes in predictions.items():
        if int(pred_class) > num_classes +1 or int(pred_class) < 0:
            continue
        if pred_class not in dict_pred.keys():
            dict_pred[pred_class] = vtk.vtkIdTypeArray()
        for index in indexes:
            dict_pred[pred_class].InsertNextValue(index)
    return dict_pred

def classification(pred_dictionnary, output_dir, num_classes, input_fiber, name_labels):

    append_list = np.ndarray(shape=num_classes, dtype=np.object)
    for i in range(num_classes):
        append_list[i] = vtk.vtkAppendPolyData()

    bundle_fiber = vtk.vtkPolyData()

    bundle_fiber = read_vtk_data(input_fiber)
    
    print (pred_dictionnary.keys())
    for pred_class in pred_dictionnary.keys():
        if vtk.VTK_MAJOR_VERSION > 5:
            append_list[int(pred_class)].AddInputData(extract_fiber(bundle_fiber, pred_dictionnary[pred_class]))
        else:
            append_list[int(pred_class)].AddInput(extract_fiber(bundle_fiber, pred_dictionnary[pred_class]))

    for num_class in range(num_classes):
        if append_list[num_class].GetInput() is None:# or num_class == 0: #if the vtk file would be empty, then don't try to write it
            print("Skipped class ",num_class," because empty")
            continue
        append_list[num_class].Update()
        write_vtk_data(append_list[num_class].GetOutput(), output_dir+'/'+name_labels[num_class]+'_extracted.vtk')
        print ("")

def run_extraction(class_data, input_fiber, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(class_data) as json_file:
        json_string = json_file.read()
        input_dict = json.loads(json_string)
    name_labels = input_dict['labels']
    predictions = input_dict['predictions']
    num_classes = len(name_labels)

    pred_dictionnary = reformat_prediction(predictions, num_classes)
    classification(pred_dictionnary, output_dir, num_classes, input_fiber, name_labels)

def main():
    args = parser.parse_args()
    run_extraction(args.class_data, args.input_fiber, args.output_dir)

if __name__ == '__main__':
    main()
