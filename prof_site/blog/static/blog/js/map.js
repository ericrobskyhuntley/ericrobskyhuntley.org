const svg = d3.select("div#author_map")
.append("svg")
    .attr("width", "100%")
.classed("map_content", true);

let prj = d3.geoOrthographic()
.rotate([76, -38, 32])
.scale(1800)

const path = d3.geoPath().projection(prj);

let affil_locs = {{person_detail.loc_geojson|safe}};

let ua = {{ua_all|safe}};
let land = {{land_all|safe}};
//let bath = {{bath_all|safe}};
//let elev = {{elev_all|safe}};

let graticule_10 = d3.geoGraticule().step([10, 10])();
let graticule_05 = d3.geoGraticule().step([5, 5])();
let graticule_01 = d3.geoGraticule().step([1, 1])();

Promise.all([ua, affil_locs, graticule_10, graticule_05, graticule_01, land, /*bath, elev*/]).then(function(data){

var symbolGenerator = d3.symbol()
     .size(100);

var land_area = svg.selectAll('path.land')
 .data(data[5].features)
 .enter()
 .append("path")
 .classed('land', true)
 .attr("d", path);

// 1 degree graticule.
var urban_area = svg.selectAll('path.ua')
  .data(data[0].features)
  .enter()
  .append("path")
  .classed('ua', true)
  .attr("d", path);

//var bath = svg.selectAll('path.bath')
//  .data([data[6]])
//  .enter()
//  .append('path')
//  .classed('bath', true)
//  .attr('d', path);

//var elev = svg.selectAll('path.elev')
//  .data([data[7]])
//  .enter()
//  .append('path')
//  .classed('elev', true)
//  .attr('d', path);

// 10 degree graticule.
var grat_10 = svg.selectAll('path.graticule_10')
  .data([data[2]])
  .enter()
  .append('path')
  .classed('graticule_10', true)
  .attr('d', path);

// 5 degree graticule.
var grat_05 = svg.selectAll('path.graticule_05')
  .data([data[3]])
  .enter()
  .append('path')
  .classed('graticule_05', true)
  .attr('d', path)
  .exit().remove();

// 1 degree graticule.
var grat_01 = svg.selectAll('path.graticule_01')
  .data([data[4]])
  .enter()
  .append('path')
  .classed('graticule_01', true)
  .attr('d', path)
  .exit().remove();

//var sphere = svg.selectAll('path.sphere')
//  .data([{type: 'Sphere'}])
//  .enter().append('path').classed('sphere', true)
//  .attr('d', path)
//  .exit().remove();

var locs = svg.selectAll("circle")
    .data(data[1].features)
  .enter()
    .append("circle")
    .attr("cx", function (d) {
      return prj(d.geometry.coordinates)[0];
    })
    .attr("cy", function (d) {
      return prj(d.geometry.coordinates)[1];
    })
    .attr("r", 4)
    .classed('locator', true);

var labels = d3.select("#author_map").selectAll("div.label")
    .data(data[1].features).enter()
    .append("div")
      .classed('label small-text', true)
      .style("position", "absolute")
      .style("opacity", 1)
      .style("left", function(d) {
        return prj(d.geometry.coordinates)[0] + "px";
      })
      .style('top', function(d) {
        return prj(d.geometry.coordinates)[1] + "px";
      })
      .html(function(d) {
        return d.properties.dpt + "<br>" + d.properties.inst + "<br>" + d.properties.city + ", " + d.properties.state;
      });

// labels.selectAll(".label")
//   .data(data[1].features)
//   .enter()
//   .append("div")
//   .style('position','absolute')
//   .style('left', function(d) {
//     return prj(d.geometry.coordinates)[0] + 10;
//   })
//   .style('top', function(d) {
//     return prj(d.geometry.coordinates)[1] - 10;
//   })
//   .text(function(d) {
//       return d.properties.inst;
//   })
//   .append('br');
})