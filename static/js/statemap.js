// height and width of map
var width = 960,
    height = 600;

// project of state map
var projection = d3.geo.albersUsa()
    .scale(1280)
    .translate([width / 2, height / 2]);

// project path of map
var path = d3.geo.path()
    .projection(projection);


// color scale that is on top of the state map
// 20 colors to choose from
var color = d3.scale.category20c().domain(d3.range(20)),
    selectedColor = 0,
    dragColor;
// when state is colored in filled state is appended to retrun list
// when page is refreshed colored states are stored
var components = color.domain().map(function() { return []; });

// append color to body where svg element of each state with attribute height and witdth
var svg = d3.select("#stateMap").append("svg")
    .attr("width", width)
    .attr("height", height);

// legend where colors are available for users to select
var legend = svg.append("g")
    .attr("class", "legend")
    .attr("transform", "translate(" + ((width - color.domain().length * 24) / 2) + ",20)")
    .style("cursor", "pointer")
  .selectAll("rect")
    .data(color.domain())
  .enter().append("rect")
    .attr("x", function(d) { return d * 24; })
    .attr("width", 24 - 3)
    .attr("height", 24 - 3)
    .style("stroke", function(d) { return d ? null : "#000"; })
    .style("fill", color)
    .on("click", clicklegend); // click on the ledgen with color

d3.select(self)
    .on("keydown", keydown)
    .node().focus();


// state map JSON data file
d3.json("/static/data/us.json", function(error, us) {
  if (error) throw error;

  var bisectId = d3.bisector(function(d) { return d.id; }).left;
  var features = topojson.feature(us, us.objects.states).features;
  console.dir(us);

  svg.append("path")
      .datum(topojson.mesh(us, us.objects.states))
      .attr("class", "background")
      .attr("d", path);



// appending colors to each state
  var merge = svg.append("g")
      .attr("class", "merge")
    .selectAll("path")
      .data(components)
    .enter().append("path")
      .style("fill", function(d, i) {
         return color(i);
       })
      .style("stroke", function(d, i) { return d3.lab(color(i)).darker(); });

  svg.append("g")
      .attr("class", "foreground")
      .style("cursor", "pointer")
      .style("stroke-opacity", .5)
    .selectAll("path")
      .data(features)
    .enter().append("path")
      .attr("d", function(d) { d.color = null; return path(d); })
      .on("mouseover", function() { this.style.stroke = "black"; })
      .on("mouseout", function() { this.style.stroke = "none"; })
      .call(d3.behavior.drag()
        .on("dragstart", dragstart)
        .on("drag", drag));

  top.location.hash.split("").slice(1, features.length).forEach(function(c, i) {
    if ((c = +c) >= 0 && c < 10) assign(features[i], c ? c - 1 : null);
  });

  redraw();

  function dragstart() {
    var feature = d3.event.sourceEvent.target.__data__;
    if (assign(feature, dragColor = feature.color === selectedColor ? null : selectedColor)) redraw();
  }

  function drag() {
    var feature = d3.event.sourceEvent.target.__data__;
    if (feature && assign(feature, dragColor)) redraw();
  }

// assign colors to state
// when state is colored in state is changed to 1
// uncolored states are are 0 meaning 0 fill and states with fill 0 --> changed to 1
//feature = state
  function assign(feature, color) {
    // added variable visit if visit is = to feature.color return true == a visited state by user

    // colors are array with indexes ie [blue1[1], blue2[2], blue3[3]]
    var state = feature; // upcode

    // if (Statevisit.color === color)  {

    //   console.log(color, Statevisit)
    //   return false; // upcode <-- retrun is done
      // null means no color if have a color and click state it removes state and its color
    // } // END
        // if state color isnt a color //!== null --> no color ==null --> colored
    // if (state.color !== null) {
    if (state.color !== null) { // if state has no color --> click state state will then be null == color
      var component = components[state.color];
      component.splice(bisectId(component, state.id), 1);
      state.color = null;
      removeStateVisit(state);
      console.log("state has no color now"); // upcode

    }

    // 1 is color 0 is null or no color
    if (color !== null) { // if color is filled
      var component = components[color];
      // Locate the insertion point for x in array to maintain sorted order ie fixed array
      component.splice(bisectId(component, state.id), 0, state);  // splace adds and removes items from the array in this case state color
      state.color = color;
      addingStateVisit(state);
      console.log("state is filled")
      console.log(state, color);  // RETURNS state id and color id



     }

    return true;



  }
// TO DO CONNECT TO SEVER USING AJAX

function showUsersVisitResults(result) {
    console.log(result);
}

function addingStateVisit(feature) {
    console.log("FEATURE.ID: " + feature.id);
    $.post("/state-map-ajax-add",
         {"feature_id":feature.id},
         showUsersVisitResults);
};

function removeStateVisit(feature) {

    $.post("/state-map-ajax-remove",
         {"feature_id":feature.id},
         showUsersVisitResults);
};

//END AJAX CALL


  function redraw() {
    merge.data(components).attr("d", function(d) { return path({type: "FeatureCollection", features: d}) || "M0,0"; });
    top.history.replaceState(null, null, "#" + features.map(function(d) { return d.color === null ? "0" : d.color + 1; }).join(""));

    }
    }); // END function


// click function for choosing a color from legend where colors are displayed
// user selects color and is able to fill in states with chosen color
function clicklegend(d) {
  legend[0][selectedColor].style.stroke = null;
  legend[0][selectedColor = d].style.stroke = "#000";
}


function keydown() {
  if (d3.event.keyCode >= 48 && d3.event.keyCode < 58) {
    var i = d3.event.keyCode - 49;
    if (i < 0) i = 20;
    clicklegend(i);
  }
}

d3.select(self.frameElement).style("height", height + "px");



var state_name_dict = {
    1: ["AL", "Alabama"],
    2: ["AK", "Alaska"],
    4: ["AZ", "Arizona"],
    5: ["AR",, "Arkansas"],
    6: ["CA", "California"],
    8: ["CO", "Colorado"],
    9: ["CT", "Connecticut"],
    10: ["DE", "Delaware"],
    11: ["DC", "District of Washington"],
    12: ["FL", "Florida"],
    13: ["GA", "Georgia"],
    15: ["HI", "Hawaii"],
    16: ["ID", "Indiana"],
    17: ["IL", "Illinois"],
    18: ["IN", "Indiana"],
    19: ["IA", "Iowa"],
    20: ["KS", "Kansas"],
    21: ["KY", "Kentucky"],
    22: ["LA", "Louisiana"],
    23: ["ME", "Maine"],
    24: ["MD", "Maryland"],
    25: ["MA", "Massachusetts"],
    26: ["MI", "Michigan"],
    27: ["MN", "Minnesota"],
    28: ["MS", "Mississippi"],
    29: ["MO", "Missouri"],
    30: ["MT", "Montana"],
    31: ["NE", "Nebraska"],
    32: ["NV", "Nevada"],
    33: ["NH", "New Hampshire"],
    34: ["NJ", "New Jersey"],
    35: ["NM", "New Mexico"],
    36: ["NY", "New York"],
    37: ["NC", "North Carolina"],
    38: ["ND", "North Dakota"],
    39: ["OH", "Ohio"],
    40: ["OK", "Oklahoma"],
    41: ["OR", "Oregon"],
    42: ["PA", "Pennsylvania"],
    44: ["RI", "Rhode Island"],
    45: ["SC", "South Carolina"],
    46: ["SD", "South Dakota"],
    47: ["TN", "Tennessee"],
    48: ["TX", "Texas"],
    49: ["UT", "Utah"],
    50: ["VT", "Vermont"],
    51: ["VA", "Virginia"],
    53: ["WA", "Washington"],
    54: ["WV", "West Virginia"],
    55: ["WI", "Wisconsin"],
    56: ["WY", "Wyoming"]
  };
