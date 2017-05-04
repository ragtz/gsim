import yaml
import numpy as np
import matplotlib.pyplot as plt



def getYamlFiles(user_id, experiment_id, num=10):
    #get worlds.yaml file
    yaml_meta_filename = "../data/user_"+str(user_id)+"/experiment_"+str(experiment_id)+"/worlds.yaml"
    #print yaml_meta_filename
    meta_files = getYamlData(yaml_meta_filename)
    return meta_files['worlds'][0:num]

"""hard coded to get all user info except for last experiment
    this corresponds to 80% train 20% test
"""  
def getYamlTrainFiles():
    num_users = 30
    exp_per_user = 5
    all_files = []
    for user_id in range(num_users):
        for exp_id in range(exp_per_user - 1):
            all_files.extend(getYamlFiles(user_id, exp_id))
    return all_files
     

"""get (x,y) of target for a certain yaml file"""
def getTargetCoordinates(yaml_file):
    data = getYamlData(yaml_file)
    return data['target'][0], data['target'][1]   

"""get (x,y) for each object in world"""
def getObjectCoordinates(yaml_file):
    data = getYamlData(yaml_file)
    objects = data['objects']
    obj_coord = []
    for obj in objects:
        #add coordinats of obj to list
        obj_coord.append((obj[0], obj[1]))

    return obj_coord
   
"""Compute displacements for a single yaml file as dictionay between features and displacements"""
def computeDisplacements(yaml_file):
    #find target and object coords
    data = getYamlData(yaml_file)
    target_coord = [data['target'][0], data['target'][1]]
    objects = data['objects']
    obj_coord = []
    displacements = {}
    for obj in objects:
        #add coordinates of obj to list associated with features
        obj_features = (obj[3],obj[4])
        displacements[obj_features] = np.array(target_coord) - np.array([obj[0], obj[1]])
    return displacements

def getAllDisplacements(yaml_files):
    all_disp = {}
    for yaml_f in yaml_files:
        #print yaml_f
        displ = computeDisplacements(yaml_f)   
        for d in displ:
            #print d
            if d not in all_disp:
                all_disp[d] = [displ[d]]
            else:
                all_disp[d].append(displ[d])
            #print all_disp
    #convert all to 2-d numpy arrays
    for f in all_disp:
        all_disp[f] = np.array(all_disp[f])
    return all_disp
         
"""takes a dictionary of feature keys with 2-d arrays of
   displacements per feature with each row a displacement 
   and plots
"""
def plotDisplacements(displacement_dict):
    plt.figure()
    colors = ['r','b','g']
    cnt = 0
    for feature in displacement_dict:
        displace_array = displacement_dict[feature]
        plt.plot(displace_array[:,0],displace_array[:,1],colors[cnt]+'o',label=feature)
        cnt += 1
    mus = getMeanDisplacements(displacement_dict)
    cnt = 0
    for f in mus:
        plt.plot(mus[f][0], mus[f][1], colors[cnt]+'x')
        cnt += 1
    
    plt.legend(loc='best')
    plt.show()

"""takes a 2-d array with each row a displacement and plots"""    
def plotDisplacementsRaw(disp_array):
   plt.figure()
   plt.plot(disp_array[:,0],disp_array[:,1],'o')
   plt.show() 

def getTotalVariances(displacement_dict):
    displ_var = {}
    for feature in displacement_dict:
        displace_array = np.array(displacement_dict[feature])
        #print displace_array.T
        displ_var[feature] = np.trace(np.cov(displace_array.T))
    return displ_var
        
def getMeanDisplacements(displacement_dict):
    displ_var = {}
    for feature in displacement_dict:
        displace_array = np.array(displacement_dict[feature])
        #print displace_array.T
        displ_var[feature] = np.mean(displace_array,0)
    return displ_var

"""returns shape-color tuple and mean displacement vector"""
def getMostLikelyLandmarkDisplacement(demo_files):
    if len(demo_files) == 1:
        #just pick randomly since all have zero variance
        all_disp = getAllDisplacements(demo_files)
        fkeys = [f for f in all_disp]
        landmark = fkeys[np.random.randint(len(fkeys))]
        return landmark, all_disp[landmark]
    else:
        #calc displacements
        all_disp = getAllDisplacements(demo_files)
        tot_vars = getTotalVariances(all_disp)  
        min_var = float("inf")
        for feature in tot_vars:
            if tot_vars[feature] < min_var:
                landmark = feature
                min_var = tot_vars[feature]
        disp_mus = getMeanDisplacements(all_disp)  

        return landmark, disp_mus[landmark]

def getYamlData(yaml_filename):
    #how to open a yaml file
    with open(yaml_filename, 'r') as stream:
        try:
            world = yaml.load(stream)
            #print world
        except yaml.YAMLError as exc:
            print exc 
            sys.exit()
    return world
    
"""return all displacements from all files in world_files
   in one big 2-d array with each row a displacement [x,y]
"""
def getAllDisplacementsConcat(world_files):
    disp_dict = getAllDisplacements(world_files)
    disp = []
    for feature in disp_dict:
        disp.extend(disp_dict[feature])
    return np.array(disp)
    


def main():
    print "grabbing files"
    #need to get a set of files for demonstrations
    #specfify user and experiment
    user_id = 5
    experiment_id = 3
    num_demos = 1
    #grab files    
    world_files = getYamlFiles(user_id, experiment_id, num_demos)
    print world_files
    #grab coordinates
    all_disp = getAllDisplacements(world_files)
    print "displacements", all_disp

#    tot_vars = getTotalVariances(all_disp)  
#    for feature in tot_vars:
#        print feature, tot_vars[feature]
#    
#    disp_mus = getMeanDisplacements(all_disp)  
#    for feature in disp_mus:
#        print feature, disp_mus[feature]
    shape_color, displacement = getMostLikelyLandmarkDisplacement(world_files)
    print "most likely landmark", shape_color
    print "displacement", displacement
    plotDisplacements(all_disp)  
    cluster_files = getYamlTrainFiles()
    train_disp = getAllDisplacementsConcat(cluster_files)
    plotDisplacementsRaw(train_disp)
    



if __name__=="__main__":
    main()
