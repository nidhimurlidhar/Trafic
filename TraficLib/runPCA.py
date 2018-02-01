import numpy as np
import argparse
import os
import tensorflow as tf
from storeDef import *
import argparse
import pickle
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import smote


def read_training(train_dir, num_landmarks, num_points, landmarks, curvature, torsion):
    dataset = []
    labels = []
    folders = [
        os.path.join(train_dir, d) for d in sorted(os.listdir(train_dir))
        if os.path.isdir(os.path.join(train_dir, d))]
    for label, folder in enumerate(folders):
        fiber_files = [
            os.path.join(folder, d) for d in sorted(os.listdir(folder))]
        for fiber in fiber_files:
            fiber_file = os.path.join(folder, fiber)
            try:
                data_fiber, data_label = fiber_extract_feature(fiber_file, landmarks, curvature, torsion,
                                                      num_landmarks, num_points, label, train=True)
                if len(data_fiber) > 0:
                  dataset.extend(data_fiber.reshape((len(data_fiber),-1)))
                  labels.extend(data_label)
            except IOError as e:
                print('Could not read:', fiber_file, ':', e, '- it\'s ok, skipping.')

    return np.array(dataset), np.array(labels)
    
def run_store(args):
    
  set_filename = os.path.join(args.train_dir, "fibers.pickle")

  if (args.pickle):
    set_filename = args.pickle

  if os.path.exists(set_filename) and not args.force:
    # You may override by setting force=True.
    print('%s already present - Skipping pickling.' % set_filename)

    with open(set_filename,'rb') as f:
      ds = pickle.load(f)

    dataset = ds["dataset"]
    labels = ds["labels"]
  else:

    save = {}
    dataset, labels = read_training(args.train_dir, args.num_landmarks, args.num_points, args.landmarks, args.curvature, args.torsion)
    save["dataset"] = dataset
    save["labels"] = labels

    with open(set_filename, 'wb') as f:
      pickle.dump(save, f)

  dataset_res,labels_res=smote.generate_with_SMOTE(dataset,labels)

  print('dataset_res',np.shape(dataset_res))
  print('labels_res',np.shape(labels_res))
  #print('labels_res',labels_res)

  PCA_plot(dataset,labels,dataset_res,labels_res)



def PCA_plot(dataset,labels,dataset_res,labels_res):

#plot original dat and data resampled after a PCA decomposition
  
  pca = PCA(n_components=100)
  pca.fit(dataset)
  dataset_pca=pca.transform(dataset)
  print('original shape: ',dataset.shape)
  print('transformed shape:',dataset_pca.shape)
  #print('Ratio variance',pca.explained_variance_ratio_)
  #plt.scatter(dataset[:,0],dataset[:,1],alpha=0.2)
  #dataset_new = pca.inverse_transform(dataset_pca)
  plt.figure(1)
  plt.subplot(121)
  plt.scatter(dataset_pca[:,0],dataset_pca[:,1],edgecolor='none',alpha=1,c=labels,cmap=plt.cm.get_cmap('nipy_spectral',len(np.unique(labels))))
  plt.title('Original data with pca (' + str(len(dataset_pca)) + ' samples)')
  
  #pca.fit(dataset_res)
  dataset_res_pca=pca.transform(dataset_res)
  
  plt.subplot(122)
  plt.scatter(dataset_res_pca[:,0],dataset_res_pca[:,1],edgecolor='none',alpha=1,c=labels_res,cmap=plt.cm.get_cmap('nipy_spectral',len(np.unique(labels_res))))
  plt.title('Resampled data with pca (' + str(len(dataset_res_pca)) + ' samples)')
  plt.colorbar()

  for i in range(1,3):
    plt.subplot(1,2,i)
    plt.xlabel('component 1')
    plt.ylabel('component 2')
  
  cumsum = np.cumsum(pca.explained_variance_ratio_)
  plt.figure(2)
  plt.plot(cumsum)
  plt.xlabel('nb of components')
  plt.ylabel('cumulative explained variance')
  plt.axhline(y=0.95, linestyle=':', label='.95 explained', color="#f23e3e")
  numcomponents = len(np.where(cumsum < 0.95)[0])
  plt.axvline(x=numcomponents, linestyle=':', label=(str(numcomponents) + ' components'), color="#31f9ad")
  plt.legend(loc=0)

  histo = np.bincount(labels)
  histo_range = np.array(range(histo.shape[0]))
  plt.figure(3)
  plt.bar(histo_range, histo)
  plt.xlabel('Groups')
  plt.ylabel('Number of samples')

  for xy in zip(histo_range, histo):
      plt.annotate(xy[1], xy=xy, ha="center", color="#4286f4")

  plt.show()



def main(_):
    parser = argparse.ArgumentParser()

    parser.add_argument(
      '--train_dir', 
      type=str,
      default='',
      help='Training directory with classes (folders), and .vtk fiber bundles')    

    parser.add_argument(
          '--pickle', 
          type=str, 
          help='Input/Output pickle file (optional)')

    parser.add_argument(
          '--num_landmarks', 
          type=int,
          default=5, 
          help='Number of landmarks computed as features')

    parser.add_argument(
          '--num_points', 
          type=int,
          default=50, 
          help='Number of points in the fiber')

    parser.add_argument(
          '--landmarks', 
          type=bool,
          default=True, 
          help='Use landmarks as features')

    parser.add_argument(
          '--curvature', 
          type=bool,
          default=True, 
          help='Use curvature as feature')
    parser.add_argument(
          '--torsion', 
          type=bool,
          default=True, 
          help='Use torsion as feature')

    parser.add_argument(
          '--force', 
          type=bool,
          default=False, 
          help='Force the pickle generation')

    FLAGS, unparsed = parser.parse_known_args()
    run_store(FLAGS)
  # Get the data.



if __name__ == '__main__':
    tf.app.run()
