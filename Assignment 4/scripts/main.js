// Read json file in global scope
let jsonDumpGlobal;
const res = await fetch('/static/data.json')
jsonDumpGlobal = await res.json();

// Extract all the floor names and element ids
let allElements = Object.keys(jsonDumpGlobal.ifc_elements)
let allFloors = Object.keys(jsonDumpGlobal.ifc_floors)

// Add initial value for each floor and element id
let calculationsGlobal = {}
for (let i = 0; i < allElements.length; i++) {
    calculationsGlobal[allElements[i]] = {
        "cost": "Nothing calculated yet.",
        "load": "Nothing calculated yet.",
        "carbon": "Nothing calculated yet."
    }
}

for (let i = 0; i < allFloors.length; i++) {
    calculationsGlobal[allFloors[i]] = {
        "cost": "Nothing calculated yet.",
        "load": "Nothing calculated yet.",
        "carbon": "Nothing calculated yet."
    }
}

// Add event listeners to the DOM and the button
document.addEventListener('DOMContentLoaded', initializeUI());
document.getElementById("calculate_button").onclick = calculateCostAndLoads

async function initializeUI() {
    // Load the table and section drawing
    createTable(jsonDumpGlobal)
    loadSectionDrawing()
}

function createTable(json_dump) {
    // Extract the unique materials from the data source
    var uniqueMaterials = json_dump.unique_materials

    // Create variables for the material property columns
    const columnNames = ["Cost\n\n[kr./m3]", "Density\n\n[kg./m3]", "Embodied Carbon\n[CO2/kg]"];
    const columnNamesShorthand = ["_cost", "_density", "_carbon"];

    // Grab the html table from the template
    let table = document.querySelector("table");

    // Upper left corner
    let row = table.insertRow();
    let cell = row.insertCell();

    // In the first row, insert the material property categories
    for (var i = 0; i < columnNames.length; i++) {
        let cell = row.insertCell();
        let text = document.createTextNode(columnNames[i]);
        cell.appendChild(text);
    }

    // Create rest of table in a nested for loop
    for (var i = 0; i < uniqueMaterials.length; i++) {

        // In the first column, add the material name
        let row = table.insertRow();
        let cell = row.insertCell();
        let text = document.createTextNode(uniqueMaterials[i]);
        cell.classList.add('material_name');

        cell.appendChild(text);

        for (var j = 0; j < columnNames.length; j++) {

            // In the remaining three columns, add the respective material property
            let cell = row.insertCell();
            let input = document.createElement("input")

            cell.appendChild(input);

            // Add material id for later retrieval
            input.id = uniqueMaterials[i] + columnNamesShorthand[j]

            // Set input value to 100
            input.value = "100"

            cell.classList.add('input_cell');
            input.classList.add('input_input');
        }
    }
}

async function loadSectionDrawing(level_name) {
    // Grab html section drawing container and reset it
    let sectionDiv = document.getElementsByClassName("section_drawing")[0]
    sectionDiv.innerHTML = ""

    // Read the raw text content of the section drawing
    var xhr = new XMLHttpRequest();
    xhr.open('GET', `static/section.html`, true);
    xhr.onreadystatechange = async function () {
        if (this.readyState !== 4) return;
        if (this.status !== 200) return;
        sectionDiv.innerHTML = this.responseText;
    };
    xhr.send();

    // Thankfully this is not a programming course
    await new Promise(r => setTimeout(r, 50));

    // Grab all svg polygons from the section drawing
    const svgDrawings = document.querySelectorAll('.ifc_floor');

    // A mouse click on one of the svg polygons will change the current 
    // selection div and also change the plan drawing accordingly
    Array.from(svgDrawings).forEach(function (svgDrawing) {
        svgDrawing.addEventListener('click', function () {
            updateCurrentSelectionWithFloor(svgDrawing.id)
            changePlanDrawing(svgDrawing.id)
        });
    });

}

async function updateCurrentSelectionWithFloor(floorId) {
    // Fetch the associated floor data
    let floorData = jsonDumpGlobal["ifc_floors"][floorId]

    // Grab the current selection div
    let currentSelectionDiv = document.getElementsByClassName("current_selection")[0]

    // Fetch the current data of the global calculation object
    let floorCost = calculationsGlobal[floorId]["cost"]
    let floorLoads = calculationsGlobal[floorId]["load"]
    let floorCarbon = calculationsGlobal[floorId]["carbon"]

    // Add this data to the current selection div
    currentSelectionDiv.innerHTML =
        `<b>${floorData["name"]}</b><br>
        Floor type: ${floorData["floor_type"]}<br>
        Floor height: ${floorData["height"]}<br>
        Cost: ${floorCost}<br>
        Loads: ${floorLoads}<br>
        Embodied carbon: ${floorCarbon}`

}

async function changePlanDrawing(floorId) {
    // Grab the plan drawing container from the html and reset it
    let planDiv = document.getElementsByClassName("plan_drawing")[0]
    planDiv.innerHTML = ""

    // Read the raw text content of the respective drawing
    var xhr = new XMLHttpRequest();
    xhr.open('GET', `static/${floorId}.html`, true);
    xhr.onreadystatechange = async function () {
        if (this.readyState !== 4) return;
        if (this.status !== 200) return;
        planDiv.innerHTML = this.responseText;
    };

    xhr.send();

    await new Promise(r => setTimeout(r, 50));

    // Grab all individual ifc elements and add event listeners to
    // each of them
    const ifcElements = document.querySelectorAll('.ifc_element');
    Array.from(ifcElements).forEach(function (ifcElement) {
        ifcElement.addEventListener('click', function () {
            updateCurrentSelectionWithElement(ifcElement.id)
        });
    });
}

async function updateCurrentSelectionWithElement(elementId) {
    // fetch data associated with currently selected ifc element
    let elementType = jsonDumpGlobal["ifc_elements"][elementId]["type"]
    let elementCost = calculationsGlobal[elementId]["cost"]
    let elementLoads = calculationsGlobal[elementId]["load"]
    let elementCarbon = calculationsGlobal[elementId]["carbon"]

    // Grab div of current selection container and update its inner HTML
    let currentSelectionDiv = document.getElementsByClassName("current_selection")[0]
    currentSelectionDiv.innerHTML = `<b>Building element</b><br>
    Element type: ${elementType}<br>
    Element id: ${elementId}<br>
    Cost: ${elementCost}<br>
    Loads: ${elementLoads}<br>
    Embodied carbon: ${elementCarbon}`
}

function parseTextFromTable() {
    // Get the table containing the user input
    var myTab = document.getElementById('user_input').rows;
    var materialsByCostDensity = {};

    // Begin iteration of the table
    for (let i = 1; i < myTab.length; i++) {
        // Retrieve text from the first column, i.e. the material name
        var materialName = myTab[i].cells[0].textContent //.replace("\n", "")
        // Retrieve text from the second column, i.e. the densities input
        var materialDensityId = (materialName + "_density").replace("\n", "");
        var materialDensity = parseFloat(document.getElementById(materialDensityId).value)

        // Retrieve text from the third column, i.e. the cost input
        var materialCostId = (materialName + "_cost").replace("\n", "");
        var materialCost = parseFloat(document.getElementById(materialCostId).value)

        // Retrieve text from the third column, i.e. the cost input
        var materialCarbonId = (materialName + "_carbon").replace("\n", "");
        var materialCarbon = parseFloat(document.getElementById(materialCarbonId).value)

        // Check for correct user input
        if (isNaN(materialCost) || isNaN(materialDensity) || isNaN(materialCarbon)) {
            alert("Incorrect input detected, try again.")
            return null;
        }

        // Update the object containing the cost and densities
        materialsByCostDensity[materialName.replace(/\n/ig, '')] = {
            "Density": materialDensity,
            "Cost": materialCost,
            "Carbon": materialCarbon,
        }

    }

    return materialsByCostDensity;
}

function calculateCostAndLoads() {
    // When button is pressed, read the user input from the table
    let materialCostDensities = parseTextFromTable()

    // Make the global calculation object contain floats and not strings
    for (let i = 0; i < allFloors.length; i++) {
        let floorName = allFloors[i]
        calculationsGlobal[floorName]["cost"] = 0
        calculationsGlobal[floorName]["load"] = 0
        calculationsGlobal[floorName]["carbon"] = 0
    }

    // Calculation results for entire building
    let finalCost = 0;
    let finalCarbon = 0;

    // Grab all elements
    let allElements = jsonDumpGlobal["ifc_elements"]

    // Begin iteration over all the elements in the building
    for (let elementId in allElements) {
        let volume = allElements[elementId]["volume"]

        // Guard clause, if the element has no volume, it is not
        // eligible for further calculations
        if (!volume) {
            continue
        }

        let materials = allElements[elementId]["materials"]

        // Initialize variables for the current element
        let elementCost = 0
        let elementLoad = 0
        let elementCarbon = 0

        for (let i = 0; i < materials.length; i++) {

            // For each material in the material list tuple, add the resulting
            // number to the element variable
            let material_name = materials[i][0]
            let material_percent = materials[i][1]

            let current_material_props = materialCostDensities[material_name]

            let currentMaterialCost = material_percent * volume * current_material_props["Cost"]
            let currentMaterialLoad = material_percent * volume * current_material_props["Density"] * 9.82
            let currentMaterialCarbon = material_percent * volume * current_material_props["Carbon"]

            elementCost += currentMaterialCost
            elementLoad += currentMaterialLoad
            elementCarbon += currentMaterialCarbon

            // Also add it to the number for the entire building
            finalCost += currentMaterialCost
            finalCarbon += currentMaterialCarbon
        }

        // Format the floor name of the current element to comply with the keys
        // found in the global object
        let currentFloor = allElements[elementId]["storey"].replace(" ", "").replace("/", "").toLowerCase()

        // Add the results to the given floor and the given element
        calculationsGlobal[currentFloor]["cost"] += Math.round(elementCost)
        calculationsGlobal[currentFloor]["load"] += Math.round(elementLoad / 1000)
        calculationsGlobal[currentFloor]["carbon"] += Math.round(elementCarbon)

        calculationsGlobal[elementId]["cost"] = Math.round(elementCost) + " kr."
        calculationsGlobal[elementId]["load"] = Math.round(elementLoad / 1000) + " kN"
        calculationsGlobal[elementId]["carbon"] = Math.round(elementCarbon) + " CO2"

    }

    // Append the units to the final results
    for (let i = 0; i < allFloors.length; i++) {
        let floorName = allFloors[i]
        calculationsGlobal[floorName]["cost"] += " kr."
        calculationsGlobal[floorName]["load"] += " kN"
        calculationsGlobal[floorName]["carbon"] += " CO2"
    }

    // Update the final cost in the HTML
    document.getElementsByClassName("analysis_results")[0].innerHTML =
        `Total cost of building: ${Math.round(finalCost)}  kr.<br>
    Total carbon footprint of building: ${Math.round(finalCarbon)} CO2`
}