# Assignment 3
### 1 Analyze the Usecase
#### 1.1 Goal
To allow for automated load calculation as well as cost estimation and thereby determination of Carbon emissions of the structural elements of any given IFC model.  

#### 1.2 Model Use
The use case is 'structural' with a focus on cost estimation and LCA of the structural elements, whereas the BIM use is within the category 'Analyse (forecast)'. The tool is primarily an aid for the Structural Engineers, where the designer has the flexibility to choose from a number of structural layout systems and check the conformance of these systems with respect to load, cost and carbon emissions associated witht the chosen elements. This makes the structural design a proactive iterative process, and enhances decision making for Structural Engineers.


### 2 Propose a (design for a) tool/workflow
#### 2.1 BPMN Workflow
<img src=" img/proposed_use_case.svg ">

#### 2.2 Detailed Description of the Workflow
The tool is programmed to extract relevant data of structural elements from a given IFC model (i.e dimensions, material properties, location of elements etc.). Using the extracted data, simple calculations are peformed to determine the parameters required for our use case (eg. volume of elements are computed from their dimensional data). The computed parameters are fed into an algorithm that takes the load, cost and carbon emissions data from a sample database, and outputs the total load, cost and carbon emissions associated which each type of element. The algorithm then checks the conformance of carbon emission with relevant codes and regulations, followed by conformance of output with given budgets and structural codes.

### 3 Information Exchange 
#### 3.1 Excel File 
#### 3.2 Description of Input Data 
1. IFC Data:
  a) Elements: The following IFC elements are relevant to our case: *IfcBeam, IfcSlab, IfcWall, IfcColumn, IfcFoundation*
  b) Properties: Material properties (material type), Dimensions (volume, location)
2. Data from external sources
  a) Cost and Carbon Emissions data from BR18
  b) Acceptable Carbon Emissions data from BR18 and structural code conformance from EN
  c) Densities for the different materials
3. Assumptions:
  a) All structural elements of the building are assumed to fall in the Ifc elements categories  listed in the section above. 
  b) The acceptable cost/budget is assumed until a real value is not provided.
  c) The load data is purely based on the weight of the structure using newtons second law.
  d) Composit details in i.e. slabs with concrete and reinforcement is simplified, to a degree where the entire slab is assumed to be concrete.

### 4 Value/Business Need of the Tool
#### 4.1 Business Value: 
The tool primarily functions as a time and cost saving tool and helps in the decision making process; for instance: in the case where the structure is not conforming to the acceptable levels of carbon emissions, the structural designer can easily evaluate which element has the most significant contribution to the carbon emissions and run a new design iteration by changing that structural element with an alternative one. The same analogy can be applied if the structure isn't conforming to set budgets or load requirements.

#### 4.2 Societal Value: 
This tool could potential help companies design structures with enhanced sustainability levels. For example, if the preliminary structure is well below specified budget, the designer can design the structure with elements having least carbon equivalence values. Hence, a simplified approach can be adopted to designing the most sustainable building while also checking whether it remains within acceptable budget or not? 

### 5 Delivery 
#### 5.1 Solving the Usecase: 
The usecase will be solved by simply having an IFC model. The analysis process itself is a completely automated process. The tool will extract required data from the loaded model and run calculations, while also checking conformance with acceptable limits.

#### 5.2 Methodology for creating the Tool: 
The tool is being created in stages and modified as each stage is completed. Initially, the tool was only used to call structural elements from a given IFC model. The next few iterations involved extracting dimensional and material data from the tool and computing volume data.

The next stage of script modification will try to incorporate a library/database for cost and carbon emissions data, and also allow for computation of LCA from volume data. The final stage will try to include validation/conformance checks specified in the BPMN process flow diagram.


