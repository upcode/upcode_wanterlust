//unreelGlobe2Map.js

var mapWidth = 960,
mapHeight = 500,
focused = false,
ortho = true,
sens = 0.25;

var projectionGlobe = d3.geo.orthographic()
.scale(240)
.center([0, 0])
.translate([mapWidth / 2, mapHeight / 2])
.clipAngle(90);

var projectionMap = d3.geo.equirectangular()
.scale(145)
.center([0, 0])
.translate([mapWidth / 2, mapHeight / 2])

var projection = projectionGlobe;

var path = d3.geo.path()
.projection(projection);

var globe2map = interpolatedProjection(projectionGlobe, projectionMap),
map2globe = interpolatedProjection(projectionMap, projectionGlobe);

var svgMap = d3.select("div#map").append("svg")
.attr("overflow", "hidden")
.attr("width", mapWidth)
.attr("height", mapHeight);

var zoneTooltip = d3.select("div#map").append("div").attr("class", "zoneTooltip"),
pointLlabel = d3.select("div#map").append("div").attr("class", "pointLabel"),
infoLabel = d3.select("div#map").append("div").attr("class", "infoLabel");

var g = svgMap.append("g");

//Unreelling transformation

function animation(interProj) {
  defaultRotate();
  g.transition()
  .duration(7500)
  .tween("projection", function() {
    return function(_) {
      interProj.alpha(_);
      g.selectAll("path").attr("d", path);
    };
  })
}

function interpolatedProjection(a, b) {
  var projection = d3.geo.projection(raw).scale(1),
  center = projection.center,
  translate = projection.translate,
  clip = projection.clipAngle,
  α;

  function raw(λ, φ) {
    var pa = a([λ *= 180 / Math.PI, φ *= 180 / Math.PI]), pb = b([λ, φ]);
    return [(1 - α) * pa[0] + α * pb[0], (α - 1) * pa[1] - α * pb[1]];
  }

  projection.alpha = function(_) {
    if (!arguments.length) return α;
    α = +_;
    var ca = a.center(), cb = b.center(),
    ta = a.translate(), tb = b.translate();
    center([(1 - α) * ca[0] + α * cb[0], (1 - α) * ca[1] + α * cb[1]]);
    translate([(1 - α) * ta[0] + α * tb[0], (1 - α) * ta[1] + α * tb[1]]);
    if (ortho === true) {clip(180 - α * 90);}
    return projection;
  };

  delete projection.scale;
  delete projection.translate;
  delete projection.center;
  return projection.alpha(0);
}

//Rotate to default before animation

function defaultRotate() {
  d3.transition()
  .duration(1500)
  .tween("rotate", function() {
    var r = d3.interpolate(projection.rotate(), [0, 0]);
    return function(t) {
      projection.rotate(r(t));
      g.selectAll("path").attr("d", path);
    };
  })
};

//Starter for function AFTER All transitions

function endall(transition, callback) {
  var n = 0;
  transition
  .each(function() { ++n; })
  .each("end", function() { if (!--n) callback.apply(this, arguments); });
}

//Loading data

queue()
.defer(d3.json, "/data/world-110m.json")
.defer(d3.tsv, "f/data/world-110m-country-names.tsv")
.await(ready);


function ready(error, world, countryData) {

  var countryById = {},
  countries = topojson.feature(world, world.objects.countries).features;

  //Adding countries by name

  countryData.forEach(function(d) {
    countryById[d.id] = d.name;
  });

  //Drawing countries on the globe

  var world = g.selectAll("path").data(countries);
  world.enter().append("path")
  .attr("class", "mapData")
  .attr("d", path)
  .classed("ortho", ortho = true);

  //Drag event

  world.call(d3.behavior.drag()
    .origin(function() { var r = projection.rotate(); return {x: r[0] / sens, y: -r[1] / sens}; })
    .on("drag", function() {
      var λ = d3.event.x * sens,
      φ = -d3.event.y * sens,
      rotate = projection.rotate();
      //Restriction for rotating upside-down
      φ = φ > 30 ? 30 :
      φ < -30 ? -30 :
      φ;
      projection.rotate([λ, φ]);
      g.selectAll("path.ortho").attr("d", path);
      g.selectAll(".focused").classed("focused", focused = false);
    }))

  //Events processing

  world.on("mouseover", function(d) {
    if (ortho === true) {
      infoLabel.text(countryById[d.id])
      .style("display", "inline");
    } else {
      zoneTooltip.text(countryById[d.id])
      .style("left", (d3.event.pageX + 7) + "px")
      .style("top", (d3.event.pageY - 15) + "px")
      .style("display", "block");
    }
  })
  .on("mouseout", function(d) {
    if (ortho === true) {
      infoLabel.style("display", "none");
    } else {
      zoneTooltip.style("display", "none");
    }
  })
  .on("mousemove", function() {
    if (ortho === false) {
      zoneTooltip.style("left", (d3.event.pageX + 7) + "px")
      .style("top", (d3.event.pageY - 15) + "px");
    }
  })
  .on("click", function(d) {
    if (focused === d) return reset();
    g.selectAll(".focused").classed("focused", false);
    d3.select(this).classed("focused", focused = d);
    infoLabel.text(countryById[d.id])
    .style("display", "inline");

    //Transforming Globe to Map

    if (ortho === true) {
      defaultRotate();
      setTimeout(function() {
        projection = globe2map;
        path.projection(projection);
        animation(projection);
        g.selectAll(".ortho").classed("ortho", ortho = false);
      }
      , 1600);
    }
  });

  //Adding extra data when focused

  function focus(d) {
    if (focused === d) return reset();
    g.selectAll(".focused").classed("focused", false);
    d3.select(this).classed("focused", focused = d);
  }

  //Reset projection

  function reset() {
    g.selectAll(".focused").classed("focused", focused = false);
    infoLabel.style("display", "none");
    zoneTooltip.style("display", "none");

    //Transforming Map to Globe

    projection = map2globe;
    path.projection(projection);
    animation(projection);
    g.selectAll("path").classed("ortho", ortho = true);
  }
};

var countryData = {
4: ["Afghanistan"],
8: ["Albania"],
12: ["Algeria"],
24: ["Angola"],
10:  ["Antarctica"],
32:  ["Argentina"],
51:  ["Armenia"],
36:  ["Australia"],
40:  ["Austria"],
31:  ["Azerbaijan"],
44:  ["Bahamas"],
50:  ["Bangladesh"],
112: ["Belarus"],
56:  ["Belgium"],
84:  ["Belize"],
204: ["Benin"],
64:  ["Bhutan"],
68:  ["Bolivia"],
70:  ["Bosnia, and Herzegovina"],
72:  ["Botswana"],
76:  ["Brazil"],
96:  ["Brunei Darussalam"],
100: ["Bulgaria"],
854: ["Burkina Faso"],
108: ["Burundi"],
116: ["Cambodia"],
120: ["Cameroon"],
124: ["Canada"],
140: ["Central African Republic"],
148: ["Chad"],
152: ["Chile"],
156: ["China"],
170: ["Colombia"],
178: ["Congo"],
180: ["The Democratic Republic of the Congo"],
188: ["Costa Rica"],
384: ["Cote d'Ivoire"],
191: ["Croatia"],
192: ["Cuba"],
196: ["Cyprus"],
203: ["Czech Republic"],
208: ["Denmark"],
262: ["Djibouti"],
214: ["Dominican Republic"],
218: ["Ecuador"],
818: ["Egypt"],
222: ["El Salvador"],
226: ["Equatorial Guinea"],
232: ["Eritrea"],
233: ["Estonia"],
231: ["Ethiopia"],
238: ["Falkland Islands"],
242: ["Fiji"],
246: ["Finland"],
250: ["France"],
260: ["French Southern Territories"],
266: ["Gabon"],
270: ["Gambia"],
268: ["Georgia"],
276: ["Germany"],
288: ["Ghana"],
300: ["Greece"],
304: ["Greenland"],
320: ["Guatemala"],
324: ["Guinea"],
624: ["Guinea-Bissau"],
328: ["Guyana"],
332: ["Haiti"],
340: ["Honduras"],
348: ["Hungary"],
352: ["Iceland"],
356: ["India"],
360: ["Indonesia"],
364: ["Iran"],
368: ["Iraq"],
372: ["Ireland"],
376: ["Israel"],
380: ["Italy"],
388: ["Jamaica"],
392: ["Japan"],
400: ["Jordan"],
398: ["Kazakhstan"],
404: ["Kenya"],
408: ["North Korea"],
410: ["South Korea"],
414: ["Kuwait"],
417: ["Kyrgyzstan"],
418: ["Democtratic Republic of Laos"],
428: ["Latvia"],
422: ["Lebanon"],
426: ["Lesotho"],
430: ["Liberia"],
434: ["Libya"],
440: ["Lithuania"],
442: ["Luxembourg"],
807: ["Macedonia"],
450: ["Madagascar"],
454: ["Malawi"],
458: ["Malaysia"],
466: ["Mali"],
478: ["Mauritania"],
484: ["Mexico"],
498: ["Moldova"],
496: ["Mongolia"],
499: ["Montenegro"],
504: ["Morocco"],
508: ["Mozambique"],
104: ["Myanmar"],
516: ["Namibia"],
524: ["Nepal"],
528: ["Netherlands"],
540: ["New Caledonia"],
554: ["New Zealand"],
558: ["Nicaragua"],
562: ["Niger"],
566: ["Nigeria"],
578: ["Norway"],
512: ["Oman"],
586: ["Pakistan"],
275: ["Palestinian Territory, Occupied"],
591: ["Panama"],
598: ["Papua New Guinea"],
600: ["Paraguay"],
604: ["Peru"],
608: ["Philippines"],
616: ["Poland"],
620: ["Portugal"],
630: ["Puerto Rico"],
634: ["Qatar"],
642: ["Romania"],
643: ["Russian Federation"],
646: ["Rwanda"],
682: ["Saudi Arabia"],
686: ["Senegal"],
688: ["Serbia"],
694: ["Sierra Leone"],
703: ["Slovakia"],
705: ["Slovenia"],
90:  ["Solomon Islands"],
706: ["Somalia"],
710: ["South Africa"],
728: ["South Sudan"],
724: ["Spain"],
144: ["Sri Lanka"],
729: ["Sudan"],
740: ["Suriname"],
748: ["Swaziland"],
752: ["Sweden"],
756: ["Switzerland"],
760: ["Syrian Arab Republic"],
158: ["Taiwan,Province of China"],
762: ["Tajikistan"],
834: ["Tanzania"],
764: ["Thailand"],
626: ["Timor-Leste"],
768: ["Togo"],
780: ["Trinidad and Tobago"],
788: ["Tunisia"],
792: ["Turkey"],
795: ["Turkmenistan"],
800: ["Uganda"],
804: ["Ukraine"],
784: ["United Arab Emirates"],
826: ["United Kingdom"],
840: ["United States"],
858: ["Uruguay"],
860: ["Uzbekistan"],
548: ["Vanuatu"],
862: ["Venezuela"],
704: ["Viet Nam"],
732: ["Western Sahara"],
887: ["Yemen"],
894: ["Zambia"],
716: ["Zimbabwe"]
};
