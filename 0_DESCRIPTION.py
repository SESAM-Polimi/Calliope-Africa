# Author: Giorgio Traverso, December 2025, Politecnico di Milano, SESAM

# This file contains a description of the project structure and its components, in particular
# the GitHub files uploaded to the SESAM group repository. All the uploaded files are part of
# my Master's Thesis work and involve the Calliope modelling of the Southern African Power 
# Pool.

# The files used for all the developed scenarios and models are organized as follows:

# 1) 1_Clustering_Codes: This folder contains all the codes used for clustering PV and wind
#    generation sites, providing as output the average generation profiles for each cluster,
#    the total installed capacity, and the representative coordinates of each cluster. The 
#    codes also include a description of the input data used, with an example provided in the
#    folder, along with the chosen degree of clustering level.

# 2) 2_Calliope_Models: This folder contains all the Calliope models developed for the 
#    Southern African Power Pool. Inside this folder, subfolders are present for each 
#    analyzed scenario, involving different configurations divided into three macro-groups:
#    autarky, existing and planned transmission, and transmission expansion scenarios 
#    (all varying the degrees of freedom related to cross-border electricity lines).

#    Each macro-group folder contains the Calliope model files. More specifically, this 
#    includes input data files in .csv format for the time series, and a YAML_Files folder 
#    containing the Calliope model configuration files in .yaml format. Each year of analysis
#    has its own folder. For the different scenarios modelled in planning mode, no additional
#    subfolders are present; instead, within the model.yaml file, it is necessary to comment 
#    or uncomment the files corresponding to the desired scenario.

# 3) 3_Post_Processing: This folder contains all the codes used for post-processing the 
#    Calliope model outputs. Inside this folder, subfolders are present for each specific 
#    result analyzed, including installed capacity, regional import/export analysis, 
#    investments, the creation of sequential .yaml files used as input files in Calliope, 
#    and finally the overall results analysis code, which provides the main results and their 
#    graphical representation.


# This description is intended to provide a general overview of the project structure and the 
# files contained in the repository. For specific details regarding the codes, input data, and 
# model configuration, please refer to the comments within the codes uploaded in the repository.
