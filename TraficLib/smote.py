from imblearn.over_sampling import SMOTE
import numpy as np 

def generate_with_SMOTE(dataset,labels):

#generate data thanks to SMOTE algorithm, it balances different groups
  sm=SMOTE(kind='regular')
  print('shape dataset',dataset.shape)
  print('shape labels',labels.shape)
  dataset_res, labels_res = sm.fit_sample(dataset,labels)
  print('shape dataset resampled',np.shape(dataset_res),'shape lables resampled',np.shape(labels_res))

  return dataset_res,labels_res