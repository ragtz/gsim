import yaml
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from nlp_class import nlp

import lfd
import gmm
import nlp_lfd

"""
This is a simple experiment setup for testing nlp+lfd with lfd.
"""





def main():
    #train on first 25 users over all experiments and test on last 5 over all experiments
    train_data = [(u,e) for u in range(25) for e in range(5)]
    test_data = [(u,e) for u in range(25,30) for e in range(5)]
    total_demos = 10  #total number of demos possible
    max_demos = 4     #maximum number of demos given to robot to learn from (the rest are used to test generalizabiltiy)
    thresh = 150
    

    ######################
    #training code here
    ######################

    #TODO learn the gmm componenets and label the data
    print "--learning gmm components--"
    gmm.labelTrainingDataDisplacements(train_data, total_demos)

    #learn groundings with training data
    print "--grounding language--"
    nlp_grounder = nlp()
    nlp_grounder.train(train_data)

    ######################
    #testing code
    ######################
    print "--testing generalization error--"
    #matrix of zeros where each row is new test case and cols are ave errors for learning from 1:max_demos demonstrations
    lfd_errors = np.zeros((len(test_data), max_demos))  
    nlp_errors = np.zeros((len(test_data), max_demos)) 
    random_errors = np.zeros((len(test_data), max_demos)) 
    aveplace_errors = np.zeros((len(test_data), max_demos)) 
    for i in range(len(test_data)):
        user_id, exp_id = test_data[i]
        for n_demos in range(1,max_demos+1):
            #get best guess of landmark and displacement using pure LfD
            lfd_shape_color, lfd_displacement = lfd.getMostLikelyLandmarkDisplacement(user_id, exp_id, n_demos)
            
            #guess landmark and displacement using NLP+LfD
            nlp_shape_color, nlp_displacement = nlp_lfd.getNLP_LfD_LandmarkDisplacementDoubleCheck(nlp_grounder, user_id, exp_id, n_demos, thresh)
            #guess placment randomly
            rand_placement = lfd.getRandomPointOnTable(user_id, exp_id, n_demos)
            #guess placement as average of demonstrated placements
            ave_placement = lfd.getMeanPlacementCoordinates(user_id, exp_id, n_demos)
      
            
            #compute accuracy over a test demo specified by demo_id
            for demo_id in range(max_demos, total_demos):
                #pure lfd error
                lfd_errors[i, n_demos-1] = nlp_lfd.averageDistanceError(lfd_shape_color, lfd_displacement, user_id, exp_id, max_demos, total_demos)
                #nlp+lfd error
                nlp_errors[i, n_demos-1] = nlp_lfd.averageDistanceError(nlp_shape_color, nlp_displacement, user_id, exp_id, max_demos, total_demos)
                #random baseline error
                random_errors[i, n_demos-1] = nlp_lfd.averageDistanceToPointError(rand_placement, user_id, exp_id, max_demos, total_demos)
                #average placement pos baseline error
                aveplace_errors[i, n_demos-1] = nlp_lfd.averageDistanceToPointError(ave_placement, user_id, exp_id, max_demos, total_demos)



    ###################
    #plot errors
    ###################
    print "lfd"
    print lfd_errors
    print "nlp"
    print nlp_errors
    yerr = 10
    plt.figure()
    plt.errorbar(range(1,max_demos+1),np.mean(lfd_errors,0), yerr=np.std(lfd_errors,0), fmt='bo-', label='lfd')
    plt.errorbar(range(1,max_demos+1),np.mean(nlp_errors,0), yerr=np.std(nlp_errors,0), fmt='g^--', label='nlp+lfd')
    plt.errorbar(range(1,max_demos+1),np.mean(random_errors,0), yerr=np.std(random_errors,0), fmt='r*-.', label='random')
    plt.errorbar(range(1,max_demos+1),np.mean(aveplace_errors,0), yerr=np.std(aveplace_errors,0), fmt='ks', linestyle='dotted', label='ave. placement')
    plt.xticks(range(1,max_demos+1))
    plt.xlabel('number of demonstrations')
    plt.ylabel('generalization L2 error')
    plt.legend(loc='best')
    plt.show()
            
 



if __name__=="__main__":
    main()
