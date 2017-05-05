import yaml
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

import lfd


"""compute the average distance error over worlds specified by user_id, exp_id, max_demos:total_demos"""
def averageDistanceError(shape_color, displacement, user_id, exp_id, max_demos, total_demos):
    sum_errors = 0.0
    #for each demo find location of shape_color
    for demo_id in range(max_demos, total_demos):
        yaml_file = lfd.getYamlFile(user_id, exp_id, demo_id)
        landmark_coord = lfd.getFeatureCoordinates(shape_color, yaml_file)
        true_coord = lfd.getPlacementCoordinates(yaml_file, user_id, exp_id)

        #add displacement
        pred_coord = np.array(landmark_coord) + np.array(displacement)

        #compare displacement to actual human placement
        sum_errors += np.linalg.norm(pred_coord - true_coord)
    return sum_errors / float(total_demos - max_demos)  

    
    



def main():
    #test over all examples
    user_exp_train = [(u,e) for u in range(30) for e in range(4)]
    user_exp_test = [(u,e) for u in range(30) for e in range(4,5)]
    total_demos = 10  #total number of demos possible
    max_demos = 6     #maximum number of demos given to robot to learn from

    ######################
    #training code here
    ######################


    ######################
    #testing code here
    ######################

    #matrix of zeros where each row is new test case and cols are ave errors for learning from 1:max_demos demonstrations
    lfd_errors = np.zeros((len(user_exp_test), max_demos))  
    for i in range(len(user_exp_test)):
        user_id, exp_id = user_exp_test[i]
        for n_demos in range(1,max_demos+1):
            #get best guess of landmark and displacement
            lfd_shape_color, lfd_displacement = lfd.getMostLikelyLandmarkDisplacement(user_id, exp_id, n_demos)
            #compute accuracy over a test demo specified by demo_id
            for demo_id in range(max_demos, total_demos):
                lfd_errors[i, n_demos-1] = averageDistanceError(lfd_shape_color, lfd_displacement, user_id, exp_id, max_demos, total_demos)



    ###################
    #plot errors
    ###################
    plt.figure()
    plt.plot(range(1,max_demos+1),np.mean(lfd_errors,0))
    plt.xlabel('number of demonstrations')
    plt.ylabel('generalization L2 error')
    plt.show()
            
 



if __name__=="__main__":
    main()
