# 11034 Advanced BIM
## Group members:
- Thor Bardrum, s193831  
- Jens Dahl Kristian, s193850  
- Kasper Fuglsang Jordt, s193801  

## Questions:
- Describe the use case you have chosen
- Who is the use case for?
- What disciplinary (non BIM) expertise did you use to solve the use case
- What IFC concepts did you use in your script (would you use in your script)
- What disciplinary analysis does it require?
- What building elements are you interested in?
- What (use cases) need to be done before you can start your use case?
- What is the input data for your use case?
- What other use cases are waiting for your use case to complete?

## Case decription
The goal of the tool made is to extract volume data from the structural elements in a IFC model in order to calculate cost and load of the structural elements in any IFC model. The use case can be of value to both expertise interested in the cost of the building as well as expertise who needs information of the self weight of the structure, the tool makes it easier to get an overview of these parameters over several iterations of the BIM model. Therefore the tool is intended for the economic and structural disciplines. In terms of disciplinary expertise, Newton's second law is used to calculate the loads of the structural elements given their density. 

The specific builings elements used in this case, are slabs, walls, beams and columns. All loadbearing elements in a standard BIM model. In order to get this use case into play, a geometry must exist for the aforementioned elements. Furthermore materials must first be granted on these elements, with defined cost and weight per volume material. When these parameters are defined from other use cases, the tool can get into play. The output of the tool will be the cost and self load of the structural elements in the BIM model. When handing this of to the structural or cost disciplines, this might result in a change to the structural elements used initially as input for the tool. E.g. if the structure is too costly or the load of the structure and live load exeeds the bearing capacity of the current static system.


