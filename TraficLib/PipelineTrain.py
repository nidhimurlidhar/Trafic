import argparse
import time
import sys
from runStore import run_store
from runTraining import run_training
from fiberfileIO import convert_time

parser = argparse.ArgumentParser()
parser.add_argument('--data_dir', action='store', dest='data_dir', help='Input directory ',
                    default="")
parser.add_argument('--lr', action='store', dest='lr', help='Learning rate for the training',
                    default='0.01')
parser.add_argument('--num_epochs', action='store', dest='num_epochs', help='Number of epochs during the training',
                    default='2')
parser.add_argument('--summary_dir', action='store', dest='summary_dir', help='Summary directory ',
                    default="")
parser.add_argument('--checkpoint_dir', action='store', dest='checkpoint_dir', help='model checkpoints directory ',
                    default="")

def run_pipeline_train(data_dir, num_epochs, lr, num_lm, summary_dir, checkpoint_dir):
	run_store(train_dir=data_dir, num_landmarks=num_lm)

	if num_lm==5:
		run_training(data_dir=data_dir, summary_dir=summary_dir,num_epochs=num_epochs, learning_rate=lr, checkpoint_dir=checkpoint_dir)
	if num_lm==32:
		run_training(data_dir=data_dir, summary_dir=summary_dir,num_epochs=num_epochs, learning_rate=lr, checkpoint_dir=checkpoint_dir)


def main():
	start = time.time()
	args = parser.parse_args()
	lr = float(args.lr)
	num_epochs = int(args.num_epochs)
	data_dir = args.data_dir
	summary_dir = args.summary_dir
	checkpoint_dir = args.checkpoint_dir
	run_pipeline_train(data_dir, num_epochs, lr, 32, summary_dir, checkpoint_dir)
	end = time.time()
	print "All training Process took %dh%02dm%02ds" % (convert_time(end - start))
	sys.stdout.flush()

if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        print ('ERROR, EXCEPTION CAUGHT')
        print str(e)
        import traceback
        traceback.print_exc()