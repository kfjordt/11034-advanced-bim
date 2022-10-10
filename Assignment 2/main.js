// This object is declared in the global scope since its properties will be dynamically updated
// Throughout the script, this is referred to as the "global object"
let loadsCostByFloors = {};

// This function is called upon loading the website
function main() {
	
	// Initialize the first prompts and reset the global variable
	plan('Click a floor to see its properties.');
	addTextToProps()
	setInitialStage()
	hideAllFloorPlans()
	
	// jQuery method executed each time an HTML entity of 'floor-' type is clicked
	$('floor-').each(function() {
		
		// In this scope, "this" is the clicked entity
		$(this).on("click", function(){

			// When a floor is clicked, read the current properties of the global object
			var floorName = $(this).attr('name')
			var floorCost = loadsCostByFloors[floorName]["Cost"]
			var floorLoad = loadsCostByFloors[floorName]["Load"]

			controlFloorplan(floorName)

			// Update the plan with the relevant information
			changePlan(formattedPlanText(floorName, floorLoad, floorCost))

		});

	});

}
function hideAllFloorPlans() {
	// Get all entities containing SVG
	var allFloors = document.getElementsByClassName("parent");

	for (var i = 0; i < allFloors.length; i++) {
		// To hide entities, set their display prop to none
		allFloors[i].style.display = "none";
	}
}
function controlFloorplan(floorName) {
	// Make sure that no overlapping will happen
	hideAllFloorPlans()

	// Select the currently pressed floor
	var selectedFloor = document.querySelectorAll('[level="' + floorName + '"]')[0];
	console.log(selectedFloor)

	// Unhide the floor plan
	selectedFloor.style.display = "block";
	
}
function setInitialStage() {
	// Find all HTML entities representing IfcSlab
	var allFloors = document.querySelectorAll('floor-[level]')

	// For each floor, update its cost and load to the initial, uncalculated state
	for (var i = 0; i < allFloors.length; i++) {
		if (allFloors[i].hasAttribute("name")) {
			var floorName = allFloors[i].getAttribute("name")

			loadsCostByFloors[floorName] = {
				"Load": "Nothing calculated yet.",
				"Cost": "Nothing calculated yet."
			}
		}
	}
}

function addTextToProps() {
	// Retrieve and add the basic IFC properties to the props1 div
	const project_name = $('project-').attr('name')
	const address = $('site-').attr('address')
	const latitude = $('site-').attr('lat')
	const longtiude = $('site-').attr('long')
	const floor_amount = document.getElementsByTagName("floor-").length;
	const site_elevation = $('site-').attr('elev')

	$('props1-').append('Project Name: '+ project_name);
	$('props1-').append('<br>');
	$('props1-').append('Address: '+ address);
	$('props1-').append('<br>');
	$('props1-').append('Latitude: '+ latitude);
	$('props1-').append('<br>');
	$('props1-').append('Longitude: '+ longtiude);
	$('props1-').append('<br>');
	$('props1-').append('Amount of floors: '+ floor_amount);
	$('props1-').append('<br>');
	$('props1-').append('Site elevation: '+ site_elevation);
}

function parseTextFromTable() {
	// Get the table containing the user input
	var myTab = document.getElementById('user_input').rows;

	var materialsByCostDensity = {};

	// Begin iteration of the table
	for (let i = 1; i < myTab.length; i++) {
		// Retrieve text from the first column, i.e. the material name
		var materialName = myTab[i].cells[0].textContent.replace("\n", "")

		// Retrieve text from the second column, i.e. the densities input
		var materialDensityId = (materialName + "_density").replace("\n", "");
		var materialDensity = parseFloat(document.getElementById(materialDensityId).value)

		// Retrieve text from the third column, i.e. the cost input
		var materialCostId = (materialName + "_cost").replace("\n", "");
		var materialCost = parseFloat(document.getElementById(materialCostId).value)

		// Check for correct user input
		if (isNaN(materialCost) || isNaN(materialDensity)) {
			alert("Incorrect input detected, try again.")
			return null;
		}
		
		// Update the object containing the cost and densities
		materialsByCostDensity[materialName.replace(/\n/ig, '')] = {
			"Density": materialDensity,
			"Cost": materialCost,
		}
		
	}

	return materialsByCostDensity;

}

function calculateCostAndLoads() {
	// When button is pressed, read the user input from the table
	var materials_cost_densities = parseTextFromTable()
	
	var finalCost = 0;

	// Update the global object to contain floats
	var floorNames = Object.keys(loadsCostByFloors)
	for (let i = 0; i < floorNames.length; i++) {
		loadsCostByFloors[floorNames[i]]["Cost"] = 0;
		loadsCostByFloors[floorNames[i]]["Load"] = 0;
	}

	// Begin iteration over element database
	for (var element in data) {
		
		// Get the storey of the current element 
		var elementFloor = data[element]["Storey"]
		
		// Begin iteration over the different material layers of the element
		for (var material in data[element]["Amounts"]) {
			
			// Fetch the amount of material present in the current element
			var materialAmount = data[element]["Amounts"][material]

			// Look up its corresponding price and density values from the user input
			var materialUnitPrice = materials_cost_densities[material]["Cost"]
			var materialUnitDensity = materials_cost_densities[material]["Density"]
			
			// Calculate the material's contribution to the price and load
			var elementPrice = materialUnitPrice * materialAmount
			var elementLoad = materialUnitDensity * materialAmount * 9.82
			
			// Update the global object with the new addition
			loadsCostByFloors[elementFloor]["Cost"] += Math.round(elementPrice);
			loadsCostByFloors[elementFloor]["Load"] += Math.round(elementLoad / 1000);
			
			// Update the final cost
			finalCost = finalCost + elementPrice

		}
	}

	// Update the final cost in the HTML
	document.getElementById("building_cost").innerHTML = ""
	$('props2result-').append('<br>Total cost of building: '+ Math.round(finalCost) + "kr.");

}

function formattedPlanText(floorName, floorLoad, floorCost) {
	// Save the formatted variables to new variables since strings are immutable
	// i.e. altering the input variables themselves is not possible
	let floorLoadFormatted = floorLoad
	let floorCostFormatted = floorCost

	// If the object contains a value other than the initial, append the proper units to the end
	if (floorLoad != "Nothing calculated yet.") {
		floorLoadFormatted = floorLoad + " kN"
		floorCostFormatted = floorCost + " kr."
	}

	// Return an HTML compatible string with line breaks
	return '<b>' + floorName + '</b>:<br> Cost: ' + floorCostFormatted +'<br> Loads: ' + floorLoadFormatted
}

// Tim's code
function plan(text) {
	jQuery('<div>', {
		id: 'plan',
		class: 'plan',
		title: 'click a floor to see the plan',
		html:text
	}).appendTo('plan-');  
}

// Tim's code
function changePlan(text) {
		$('#plan').html(text);
	}
	