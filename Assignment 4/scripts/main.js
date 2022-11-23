async function main() {
    let json_dump;

    const res = await fetch('/static/data.json')
    json_dump = await res.json();

    createTable(json_dump)
    createSectionView(json_dump)
}

function createTable(json_dump) {
    var unique_materials = json_dump.building.unique_materials
    
    const column_names = ["Cost\n\n[kr./m3]", "Density\n\n[kg./m3]", "Embodied Carbon\n[CO2/kg]"];

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
            
            input.value = "100"

            cell.classList.add('input_cell');
            input.classList.add('input_input');
        }
    }
    
      
}

function createSectionView(json_dump) {
    const section_drawing_container = document.getElementsByClassName("section_drawing")[0];
    const section_drawing = document.createElementNS('http://www.w3.org/2000/svg', 'svg');

    var floors = json_dump.building.ifc_floors
    
    let totalHeight = 0;
    for (const value of Object.values(floors)) {
        totalHeight += value["height"];
    }
    
    var startY = 100;
    
    for (const value of Object.entries(floors)) {
        const floor = document.createElementNS('http://www.w3.org/2000/svg','rect');
        
        var floorName = value[0];
        var floorProps = value[1];
        
        var percentHeight = Math.round(100 * (floorProps["height"] / totalHeight))

        floor.setAttribute('width', "80%");
        floor.setAttribute('height', percentHeight + "%");
        floor.setAttribute('x', '10%');
        floor.setAttribute('y', startY - percentHeight + "%");
        
        floor.setAttribute('stroke', 'black');
        floor.setAttribute('fill', 'white');

        const floorTitle = document.createElementNS('http://www.w3.org/2000/svg','text');
        floorTitle.setAttribute("y", startY  + "%")
        floorTitle.setAttribute("x", "10%")
        floorTitle.innerHTML = floorName

        section_drawing.appendChild(floorTitle);
        section_drawing.appendChild(floor);
        console.log("Start y: " + startY)
        console.log("Height: " + percentHeight)
        console.log("")
        startY -= percentHeight;
    }


    section_drawing_container.appendChild(section_drawing)
}
document.addEventListener('DOMContentLoaded', main());