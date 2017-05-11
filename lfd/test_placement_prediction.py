import yaml
import numpy as np
import matplotlib.pyplot as plt
import random
import lfd
import nlp_lfd



user_id = 26      #user to test on 
exp_id = 0        #experiment id to test on 
num_demos = 1     #train on demos in range(0,num_demos)
test_demo_id = 5  #demonstration id for testing, any number in range(num_demos,10)
train_data = [(u,e) for u in range(25) for e in range(5)]  #training data for nlp system, this trains on first 25 users for all experiments

###example of LfD placement prediction
#call this method to get list [x,y] for placement
lfd_location = lfd.getPredictedPlacementLocation(user_id, exp_id, num_demos, test_demo_id)
print "predicted placement location for lfd is", lfd_location


###example of NLP+LfD placement prediction
nlp_location = nlp_lfd.getPredictedPlacementLocation(train_data, user_id, exp_id, num_demos, test_demo_id)
print "predicted placement location for lfd is", nlp_location
