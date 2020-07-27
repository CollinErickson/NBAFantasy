# -*- coding: utf-8 -*-
"""
Created on Fri Jun 03 17:42:08 2016

@author: cbe117
"""

import lasagne
import theano
import theano.tensor as T
import numpy
import random
import pylab
import numpy as np
from scipy.stats import threshold
import timeit

numpy.random.seed(123)
lasagne.random.set_rng(numpy.random.RandomState(456))
random.seed(789)


try:
    X_train
except NameError:
    #train_nbafilepath = 'C://Users//cbe117//School//IEMS490//Project//train1.csv'
    #test_nbafilepath = 'C://Users//cbe117//School//IEMS490//Project//test1.csv'
    #train_nbafilepath = 'C://Users//cbe117//School//IEMS490//Project//train5.csv'
    #test_nbafilepath = 'C://Users//cbe117//School//IEMS490//Project//test5.csv'
    train_nbafilepath = 'data//train6.csv'
    test_nbafilepath = 'data//test6.csv'
    train = np.loadtxt(train_nbafilepath,delimiter=',',skiprows=1)
    test = np.loadtxt(test_nbafilepath,delimiter=',',skiprows=1)
    train = train.astype('float32')#[2000:2600,:]
    test  = test.astype('float32')
    X_train = train[:,1:]
    X_test  = test[:,1:]
    y_train = train[:,0]#np.array(y[train_inds])
    y_test  = test[:,0]#y_train.reshape((y_train.shape[0]))
    y_train_orig = (train[:,0])#.astype(int)
    y_test_orig  = (test[:,0])#.astype(int)
    
    # To get classes
    def num_to_class(nparr):
        t1 = np.round(nparr)
        t1 = threshold(t1,0,60)
        return t1.astype('int')
    y_train = num_to_class(y_train)
    y_test  = num_to_class(y_test)
    y_train_class = num_to_class(y_train)
    y_test_class  = num_to_class(y_test)
    y_train_class_sqrt = np.sqrt(y_train_class)
    #y_test_class  = num_to_class(y_test)
    
num_classes = np.max((np.max(y_train),np.max(y_test))) - np.min((np.min(y_train),np.min(y_test))) + 1
num_classes = np.max((np.max(y_train_class),np.max(y_test_class))) - np.min((np.min(y_train_class),np.min(y_test_class))) + 1
num_classes = 61
range_classes = np.array(range(num_classes))

num_fea = X_train.shape[1]
num_dp  = X_train.shape[0]


input_var = T.matrix()
target_var = T.ivector()

#Initialize the network
network = lasagne.layers.InputLayer((None,num_fea), input_var)

LOGISTIC_REGRESSION = False

#TODO: Add layers including the softmax layer
#if LOGISTIC_REGRESSION:
#    network = lasagne.layers.DenseLayer(
#     network, num_units=num_classes, nonlinearity=lasagne.nonlinearities.sigmoid)
#else:
# NN with two hidden layers
# First hidden layer is dense with 10 units using tanh
network = lasagne.layers.DenseLayer(network, num_units=100, nonlinearity=lasagne.nonlinearities.leaky_rectify)
network = lasagne.layers.DenseLayer(network, num_units=50, nonlinearity=lasagne.nonlinearities.leaky_rectify)
# Second hidden layer is dense with 8 units using sigmoid
network = lasagne.layers.DenseLayer(network, num_units=50, nonlinearity=lasagne.nonlinearities.leaky_rectify)
network = lasagne.layers.DenseLayer(network, num_units=50, nonlinearity=lasagne.nonlinearities.leaky_rectify)

# Output layer is dense using softmax
network = lasagne.layers.DenseLayer(
 network, num_units=num_classes, nonlinearity=lasagne.nonlinearities.softmax)
 
#This gives the probabilities
prediction = lasagne.layers.get_output(network)
test_prediction = lasagne.layers.get_output(network, deterministic=True)
predict_fn = theano.function([input_var], T.argmax(test_prediction, axis=1))
predict_fn_all = theano.function([input_var], test_prediction)
#loss = lasagne.objectives.categorical_crossentropy(prediction, target_var)
loss = lasagne.objectives.categorical_crossentropy(prediction, target_var).mean()
#loss = lasagne.objectives.squared_error(prediction.T, target_var).mean()
#loss = lasagne.objectives.aggregate(theano.numpy.power(prediction.T - target_var,2),mode='mean')#.mean()
#lasagne.objectives.categorical_crossentropy(network_output.reshape((-1, 46)), target_var.flatten())
#loss = loss.mean() + 1e-4 * lasagne.regularization.regularize_network_params(
#        network, lasagne.regularization.l2)
get_loss = theano.function([input_var,target_var],loss)
#objective = lasagne.objectives.Objective(
# l_output,
 # categorical_crossentropy computes the cross-entropy loss where the network
 # output is class probabilities and the target value is an integer denoting the class.
# loss_function=lasagne.objectives.categorical_crossentropy)
# get_loss computes a Theano expression for the objective, given a target variable
# By default, it will use the network's InputLayer input_var, which is what we want.
#loss = objective.get_loss(target=target_var)


BATCH_SIZE = 100 #TODO: Your choice
NUM_BATCHES = X_train.shape[0]/BATCH_SIZE
STEP_SIZE = .00001  #TODO: Your choice
JITTER = True

#These are all the parameters of the network
params = lasagne.layers.get_all_params(network,trainable=True)

#updates = lasagne.updates.nesterov_momentum(
#        loss, params, learning_rate=0.01, momentum=0.9)
#updates = lasagne.updates.sgd(loss,params,learning_rate = STEP_SIZE)
updates = lasagne.updates.adam(loss,params,learning_rate = STEP_SIZE)

train_fn = theano.function([input_var, target_var], loss, updates=updates)

#TODO: Define and compile the loss, gradient and accuracy functions


num_epochs = 30000
max_time = 120*60

losses_train = [get_loss(X_train,y_train)]
losses_test  = [get_loss(X_test,y_test)]
#accuracy_train = [1.*sum(predict_fn(X_train) == y_train)/y_train.shape[0]]
#accuracy_test= [1.*sum(predict_fn(X_test) == y_test)/y_test.shape[0]]
accuracy_train= [np.mean(np.power(predict_fn(X_train) - y_train,2))]
accuracy_test = [np.mean(np.power(predict_fn(X_test ) - y_test ,2))]
best_train_loss = np.Inf
best_train_acc = np.Inf
best_test_acc = np.Inf
start_time = timeit.default_timer()
for epoch in xrange(num_epochs):
    if max_time != None:
        if timeit.default_timer() - start_time > max_time:
            break
    loss_train = 0
    for b in range(NUM_BATCHES):
        indices = random.sample(range(X_train.shape[0]),BATCH_SIZE)
        #Compute SG on these indices and take the SGD step
        if not JITTER: # use plain y values
            loss_train += train_fn(X_train[indices,:], (y_train[indices]))
        else: # jitter y values to get more robust solution
            loss_train += train_fn(X_train[indices,:], 
                                   num_to_class(y_train_orig[indices] + np.random.normal(0,.5,BATCH_SIZE) * y_train_class_sqrt[indices]))
    #losses_train.append(loss_train)
            
    # do losses
    train_loss = get_loss(X_train,y_train)
    test_loss = get_loss(X_test,y_test)
    losses_train.append(train_loss)
    losses_test.append(test_loss)
    best_train_loss = min(train_loss,best_train_loss)
    
    # do MSE's
    train_pred_mat = predict_fn_all(X_train)
    train_pred_means = np.sum(train_pred_mat * range_classes[np.newaxis,:],axis=1)
    acc_train = np.mean(np.power(train_pred_means - y_train,2))
    accuracy_train.append(acc_train)
    best_train_acc = min(acc_train,best_train_acc)
    test_pred_mat = predict_fn_all(X_test)
    test_pred_means = np.sum(test_pred_mat * range_classes[np.newaxis,:],axis=1)
    acc_test = np.mean(np.power(test_pred_means - y_test,2))
    accuracy_test.append(acc_test)
    best_test_acc = min(acc_test,best_test_acc)
    #accuracy_train.append(1.*sum(predict_fn(X_train) == y_train)/y_train.shape[0])
    #accuracy_test.append(1.*sum(predict_fn(X_test) == y_test)/y_test.shape[0])
    #print loss_train, get_loss(X_train,y_train)
    #print("Epoch %4d:\tLoss %g\t%8d\t%d\t%d\t%d\t%d" % (epoch + 1, loss_train ,sum(predict_fn(X_train) == y_train),y_train.shape[0],sum(predict_fn(X_test) == y_test),y_test.shape[0],sum(predict_fn(X_train)==0)))
    print "Epoch %4d:   %.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.1f" % (epoch + 1, train_loss, best_train_loss, acc_train,acc_test,best_train_acc,best_test_acc,timeit.default_timer() - start_time)
end_time = timeit.default_timer()
print 'Run time is %.1f sec'%(end_time - start_time)
print best_train_loss,best_train_acc,best_test_acc,end_time-start_time

# plot loss / categorical cross entropy
pylab.figure()
pylab.plot(range(len(losses_train)),losses_train,linewidth=5)
pylab.plot(range(len(losses_test)),losses_test,linewidth=3)
pylab.title('Loss for ' + ('logistic regression' if LOGISTIC_REGRESSION else 'neural network') + ', n_train = %d'%(num_dp/2))
pylab.xlabel('Epoch')
pylab.ylabel('Cross entropy')
pylab.legend(['Train','Test'],loc=1)
pylab.tight_layout()
pylab.show()

# Plot MSE
pylab.figure()
pylab.plot(range(len(accuracy_train)),accuracy_train,linewidth=5)
pylab.plot(range(len(accuracy_test)),accuracy_test,linewidth=3)
pylab.title('Mean squared error for ' + ('logistic regression' if LOGISTIC_REGRESSION else 'neural network') + ', n_train = %d'%(num_dp/2))
pylab.xlabel('Epoch')
pylab.ylabel('MSE')
pylab.legend(['Train','Test'],loc='upper right')
#pylab.ylim((-.1,1.1))
pylab.tight_layout()
pylab.show()

# plot predicted vs actual
pylab.figure()
pylab.scatter(y_train+np.random.uniform(-.5,.5,y_train.shape),train_pred_means,c='blue',s=2,marker='x',edgecolors='face')
pylab.scatter(y_test+np.random.uniform(-.5,.5,y_test.shape),test_pred_means,c='orangered',s=1,marker='o',edgecolors='face')
pylab.title('Predicted vs actual for ' + ('logistic regression' if LOGISTIC_REGRESSION else 'neural network') + ', n_train = %d'%(num_dp/2))
pylab.xlabel('Actual value')
pylab.ylabel('Predicted value')
pylab.legend(['Train','Test'],loc=4)
#pylab.ylim((-.1,1.1))
pylab.tight_layout()
pylab.show()



# use trained network for predictions
test_prediction = lasagne.layers.get_output(network, deterministic=True)
predict_fn = theano.function([input_var], T.argmax(test_prediction, axis=1))
print 'Correct predictions: ',sum(predict_fn(X_test) == y_test),'of',len(y_test)
#print("Predicted class for first test input: %r" % predict_fn(test_data[0]))


# 3.26, 181 with 1 leakrec of 200 after 300 epochs
# 3.35, 196 2 leakred 500 200 after 100 epochs .00001
#   3.28, 1.86 after 300 epochs, not much improvement
# 3.17, 158.64+154.65, 200x100 leaky, 2400 epochs, 100 minutes, slow progress at end, predictions still 0-20 or 30
#   These were SGD BAD
# Switching to Adam
# 20x20x20 leaky 3.62 172+166 100 sec 50 epochs
# 20x20x20 leaky 2.89 88+94 1000 sec 500 epochs