# Group 01 
## Reflections on our work
We chose to build an audit tool for consulting engineers to monitor the impact of the different material choices in the project. This was done with respect to the cost, structural calculations and the carbon emissions of the building. The tool itself needs quite a bit of work for it to be functional - mainly establishing a link to a Speckle stream which would promote good data culture in the project (i.e. everyone having access to the same data/single source of truth) and preserve the version history of all the material data.

If future work were to be conducted, it would make good sense to port the project to a JS library/framework instead of doing everything in native JavaScript. For instance, React would be a good choice because of the UI heavy nature of a BIM application. For handling the IFC parts of the application, the framework IFC.js would be optimal to use to parse the IFC files, thereby eliminating the need for Python and making the application purely web-based.

