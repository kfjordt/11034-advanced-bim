# Assignment 3
### 1 Analyze the Usecase
#### 1.1 Goal
To allow for automated cost estimation and determination of Carbon emissions of the structural elements of any given IFC model.  

#### 1.2 Model Use
The Usecase is 'structural' with a focus on cost estimation and LCA of the structural elements, whereas the BIM use is within the category 'Analyse (forecast)'. The tool is primarily an aid for the Structural Engineers, where the designer has the flexibility to choose from a number of structural layout systems and check the conformance of these systems with respect to cost and carbon emissions associated witht the chosen elements. This makes the structural design a proactive iterative process, and enhances decision making for Structural Engineers.   


### 2 Propose a (design for a) tool/workflow
#### 2.1 BPMN Workflow
<img src=" img/proposed_use_case.svg ">

#### 2.2 Detailed Description of the Workflow
The tool is programmed to extract relevant data of structural elements from a given IFC model (i.e dimensions, material properties, location of elements etc.). Using the extracted data, simple calculations are peformed to determine the parameters required for our usecase (eg. volume of elements are computed from their dimensional data). The computed parameters are fed into an algorithm that takes the cost and carbon emissions data from a sample database, and outputs the total cost and carbon emissions associated which each type of element. The algorithm then checks the conformance of carbon emission with relevant codes and regulations, followed by conformance of output with given budgets and structural codes.

### 3 Information Exchange 
#### 3.1 Excel File 
#### 3.2 Description of Input Data 
1. IFC Data:
  a) Elements: The following IFC elements are relevant to our case: *IfcBeam, IfcSlab, IfcWall,   IfcColumn, IfcFoundation*
  b) Properties: Material properties (), Dimensions ()
2. Data from external sources
  a) Cost and Carbon Emissions data from BR18
3. Assumptions:
  a) All structural elements of the building are assumed to fall in the Ifc elements categories  listed in the section above. 
  b) ANY ASSUMPTIONS ABOUT LOAD DATA??

### 4 Value/Business Need of the Tool
#### 4.1 Business Value: The use case can be of value to both expertise interested in the cost of the building as well as expertise who needs information of the self weight of the structure, the tool makes it easier to get an overview of these parameters over several iterations of the BIM model.

#### 4.2 Societal Value: 

## Delivery 
### Our tool as a solution for our Usecase
### Methodology for creating the Tool


