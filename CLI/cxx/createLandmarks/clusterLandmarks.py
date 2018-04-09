import os
import csv
import argparse
from sklearn.cluster import AffinityPropagation

parser = argparse.ArgumentParser()
parser.add_argument('--input', action='store', dest='input', help='Input landmarks file (.fcsv)', default='')
parser.add_argument('--output', action='store', dest='output', help='Output landmarks file (.fcsv)', default='')

def parse_fcsv_input(filename):
    with open(filename, 'r') as csvfile:
        input_list = csv.reader(csvfile)
        array = []
        for row in input_list:
            array.append(row)
    return array

def output_landmarks(filename, landmarks):
	output_string = '# Markups fiducial file version = 4.5\n# CoordinateSystem = 0\n# Columns = id,x,y,z,ow,ox,oy,oz,vis,sel,lock,label,desc,associatedNodeID\n'
	index = 0
	for landmark in landmarks:
		output_string += 'Landmark_' + str(index) + ',' + str(landmark[0]) + ',' + str(landmark[1]) + ',' + str(landmark[2]) + ',0,0,0,1,1,1,0,LM-' + str(index + 1) + ',,\n'
		index += 1
	print (output_string)
	with open(filename, 'w') as fcsvfile:
		fcsvfile.write(output_string)

def main():

	args = parser.parse_args()
	input_file = args.input
	output_file = args.output

	array = parse_fcsv_input(input_file)

	X = []
	for row in array:
		if row[0][0] == '#':
			continue
		landmark = []
		landmark.append(float(row[1]))
		landmark.append(float(row[2]))
		landmark.append(float(row[3]))
		X.append(landmark)

	af = AffinityPropagation().fit(X)

	cluster_centers_indices = af.cluster_centers_indices_
	n_clusters = len(cluster_centers_indices)
	print('Estimated number of clusters: %d' % n_clusters)

	Y = []
	for i in range(n_clusters):
		center = X [cluster_centers_indices[i]]
		Y.append(center)

	output_landmarks(output_file, Y)



if __name__ == '__main__':
    main()