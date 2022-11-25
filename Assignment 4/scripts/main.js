let json_dump_global;

const res = await fetch('/static/data.json')
json_dump_global = await res.json();

let allElements = Object.keys(json_dump_global.ifc_elements)
let allFloors = Object.keys(json_dump_global.ifc_floors)

let calculations__global = {}

for (let i = 0; i < allElements.length; i++) {
    calculations__global[allElements[i]] = {
        "cost": "Nothing calculated yet.",
        "load": "Nothing calculated yet.",
        "carbon": "Nothing calculated yet."
    }
}

for (let i = 0; i < allFloors.length; i++) {
    calculations__global[allFloors[i]] = {
        "cost": "Nothing calculated yet.",
        "load": "Nothing calculated yet.",
        "carbon": "Nothing calculated yet."
    }
}


document.addEventListener('DOMContentLoaded', main());
document.getElementById("calculate_button").onclick = calculateCostAndLoads

async function main() {
    let json_dump;

    const res = await fetch('/static/data.json')
    json_dump = await res.json();

    createTable(json_dump)

    loadDrawings("section")

}

function createTable(json_dump) {
    var unique_materials = json_dump.unique_materials

    const column_names = ["Cost\n\n[kr./m3]", "Density\n\n[kg./m3]", "Embodied Carbon\n[CO2/kg]"];
    const column_names_shorthand = ["_cost", "_density", "_carbon"];

    let table = document.querySelector("table");

    let row = table.insertRow();
    let cell = row.insertCell();

    for (var i = 0; i < column_names.length; i++) {
        let cell = row.insertCell();
        let text = document.createTextNode(column_names[i]);
        cell.appendChild(text);
    }

    for (var i = 0; i < unique_materials.length; i++) {
        let row = table.insertRow();
        let cell = row.insertCell();
        let text = document.createTextNode(unique_materials[i]);
        cell.classList.add('material_name');

        cell.appendChild(text);

        for (var j = 0; j < column_names.length; j++) {
            let cell = row.insertCell();
            let input = document.createElement("input")

            cell.appendChild(input);

            input.id = unique_materials[i] + column_names_shorthand[j]
            input.value = "100"

            cell.classList.add('input_cell');
            input.classList.add('input_input');
        }
    }


}

async function loadDrawings(level_name) {
    let section_div = document.getElementsByClassName("section_drawing")[0]

    section_div.innerHTML = ""

    var xhr = new XMLHttpRequest();
    xhr.open('GET', `static/${level_name}.html`, true);
    xhr.onreadystatechange = async function () {
        if (this.readyState !== 4) return;
        if (this.status !== 200) return;
        section_div.innerHTML = this.responseText;
    };

    xhr.send();

    // Thankfully this is not a programming course
    await new Promise(r => setTimeout(r, 50));

    const svgDrawings = document.querySelectorAll('.ifc_floor');

    Array.from(svgDrawings).forEach(function (svgDrawing) {
        svgDrawing.addEventListener('click', function () {
            updateCurrentSelectionWithFloor(svgDrawing.id)
            changePlanDrawing(svgDrawing.id)
        });
    });

}

async function updateCurrentSelectionWithFloor(floorId) {
    let floor_data = json_dump_global["ifc_floors"][floorId]

    let current_selecton_div = document.getElementsByClassName("current_selection")[0]

    let floorCost = calculations__global[floorId]["cost"]
    let floorLoads = calculations__global[floorId]["load"]
    let floorCarbon = calculations__global[floorId]["carbon"]

    current_selecton_div.innerHTML =

    `<b>${floor_data["name"]}</b><br>
    Floor type: ${floor_data["floor_type"]}<br>
    Floor height: ${floor_data["height"]}<br>
    Cost: ${floorCost}<br>
    Loads: ${floorLoads}<br>
    Embodied carbon: ${floorCarbon}`

}

async function changePlanDrawing(floorId) {

    let plan_div = document.getElementsByClassName("plan_drawing")[0]

    plan_div.innerHTML = ""

    var xhr = new XMLHttpRequest();
    xhr.open('GET', `static/${floorId}.html`, true);
    xhr.onreadystatechange = async function () {
        if (this.readyState !== 4) return;
        if (this.status !== 200) return;
        plan_div.innerHTML = this.responseText;
    };

    xhr.send();

    await new Promise(r => setTimeout(r, 50));

    const ifcElements = document.querySelectorAll('.ifc_element');

    Array.from(ifcElements).forEach(function (ifcElement) {
        ifcElement.addEventListener('click', function () {
            updateCurrentSelectionWithElement(ifcElement.id)
        });
    });
}

async function updateCurrentSelectionWithElement(elementId) {
    let elementType = json_dump_global["ifc_elements"][elementId]["type"]
    let elementCost = calculations__global[elementId]["cost"]
    let elementLoads = calculations__global[elementId]["load"]
    let elementCarbon = calculations__global[elementId]["carbon"]

    let current_selecton_div = document.getElementsByClassName("current_selection")[0]

    current_selecton_div.innerHTML = `<b>Building element</b><br>
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
    let materials_cost_densities = parseTextFromTable()
 
    for (let i = 0; i < allFloors.length; i++) {
        let floorName = allFloors[i]
        calculations__global[floorName]["cost"] = 0
        calculations__global[floorName]["load"] = 0
        calculations__global[floorName]["carbon"] = 0
    }

    let finalCost = 0;
    let finalCarbon = 0;

    let allElements = json_dump_global["ifc_elements"]

    for (let elementId in allElements) {
        let volume =  allElements[elementId]["volume"]

        if (!volume) {
            continue
        }

        let materials = allElements[elementId]["materials"]

        let elementCost = 0
        let elementLoad = 0
        let elementCarbon = 0

        for (let i = 0; i < materials.length; i++) {
            
            let material_name = materials[i][0]
            let material_percent = materials[i][1]
            
            let current_material_props  = materials_cost_densities[material_name]
            
            let currentMaterialCost = material_percent * volume * current_material_props["Cost"]
            let currentMaterialLoad = material_percent * volume * current_material_props["Density"] * 9.82
            let currentMaterialCarbon = material_percent * volume * current_material_props["Carbon"]
            
            elementCost += currentMaterialCost
            elementLoad += currentMaterialLoad
            elementCarbon += currentMaterialCarbon
            
            finalCost += currentMaterialCost
            finalCarbon += currentMaterialCarbon
        }
        
        let currentFloor = allElements[elementId]["storey"].replace(" ", "").replace("/","").toLowerCase()

        calculations__global[currentFloor]["cost"] += Math.round(elementCost)
        calculations__global[currentFloor]["load"] += Math.round(elementLoad / 1000)
        calculations__global[currentFloor]["carbon"] += Math.round(elementCarbon)

        calculations__global[elementId]["cost"] = Math.round(elementCost) + " kr."
        calculations__global[elementId]["load"] = Math.round(elementLoad / 1000) + " kN"
        calculations__global[elementId]["carbon"] = Math.round(elementCarbon) + " CO2"
        
    }

    for (let i = 0; i < allFloors.length; i++) {
        let floorName = allFloors[i]
        calculations__global[floorName]["cost"] += " kr."
        calculations__global[floorName]["load"] += " kN"
        calculations__global[floorName]["carbon"] += " CO2"
    }

    // Update the final cost in the HTML
    document.getElementsByClassName("analysis_results")[0].innerHTML = 
    `Total cost of building: ${Math.round(finalCost)}  kr.<br>
    Total carbon footprint of building: ${Math.round(finalCarbon)} CO2`
}