<template>
  <div style="margin: 50px; 0;">
    <a-button
      style="margin-left: 5px; margin-top: 50px; float: left;"
      type="primary"
      @click="removeChart()"
    >Eliminar Grafico</a-button>
    <div ref="chart" />
  </div>
</template>

<script>
import * as d3 from "d3";
import rendering from "@/utils/rendering";
import types from "@/utils/types";
import moment from "moment";
import { Button } from "ant-design-vue";
import _ from 'lodash';

const utils = { ...rendering, ...types };

export default {
  props: {
    niceTable: {
      type: Object,
      required: true
    },
    conf: {
      type: Object,
      required: true
    }
  },

  components: {
    "a-button": Button
  },

  computed: {
    backend() {
      return this.niceTable.getBackend();
    },

    columns() {
      return this.niceTable ? this.niceTable.getVisibleColumns() : [];
    },

    rows() {
      let niceTableRows = this.niceTable.getRows();
      let selectedRows = this.conf.selectedRows;
      return niceTableRows.filter(
        row => selectedRows.indexOf(niceTableRows.indexOf(row)) >= 0
      );
    }
  },

  mounted() {
    let data = this.transformData();
    this.draw(data);
  },

  methods: {
    // Rendering
    draw(data) {
      var margin = {
          top: 20,
          right: 80,
          bottom: 30,
          left: 50
        },
        width = 900 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

      // var parseDate = d3.time.format("%Y%m%d").parse;

      var x = d3.time.scale().range([0, width]);

      var y = d3.scale.linear().range([height, 0]);

      var color = d3.scale.category10();

      var xAxis = d3.svg
        .axis()
        .scale(x)
        .orient("bottom");

      var yAxis = d3.svg
        .axis()
        .scale(y)
        .orient("left");

      var line = d3.svg
        .line()
        .interpolate("basis")
        .x(function(d) {
          return x(d.date);
        })
        .y(function(d) {
          return y(d.value);
        });

      var svg = d3
        .select(this.$refs.chart)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      // var data = d3.tsv.parse(myData);

      color.domain(
        d3.keys(data[0]).filter(function(key) {
          return key !== "date";
        })
      );

      // data.forEach(function(d) {
      //   d.date = parseDate(d.date);
      // });

      data = _.sortBy(data, ["date"]);

      var yValues = color.domain().map(function(name) {
        return {
          name: name,
          values: data.map(function(d) {
            return {
              date: d.date,
              value: +d[name]
            };
          })
        };
      });

      x.domain(
        d3.extent(data, function(d) {
          return d.date;
        })
      );

      y.domain([
        d3.min(yValues, function(c) {
          return d3.min(c.values, function(v) {
            return v.value;
          });
        }),
        d3.max(yValues, function(c) {
          return d3.max(c.values, function(v) {
            return v.value;
          });
        })
      ]);

      var legend = svg
        .selectAll("g")
        .data(yValues)
        .enter()
        .append("g")
        .attr("class", "legend");

      legend
        .append("rect")
        .attr("x", width - 20)
        .attr("y", function(d, i) {
          return i * 20;
        })
        .attr("width", 10)
        .attr("height", 10)
        .style("fill", function(d) {
          return color(d.name);
        });

      legend
        .append("text")
        .attr("x", width - 8)
        .attr("y", function(d, i) {
          return i * 20 + 9;
        })
        .text(function(d) {
          return d.name;
        });

      svg
        .append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

      svg
        .append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end");

      var yValue = svg
        .selectAll(".yValue")
        .data(yValues)
        .enter()
        .append("g")
        .attr("class", "yValue");

      yValue
        .append("path")
        .attr("class", "line")
        .attr("d", function(d) {
          return line(d.values);
        })
        .style("stroke", function(d) {
          return color(d.name);
        });

      var mouseG = svg.append("g").attr("class", "mouse-over-effects");

      mouseG
        .append("path") // this is the black vertical line to follow mouse
        .attr("class", "mouse-line")
        .style("stroke", "black")
        .style("stroke-width", "1px")
        .style("opacity", "0");

      var lines = document.getElementsByClassName("line");

      var mousePerLine = mouseG
        .selectAll(".mouse-per-line")
        .data(yValues)
        .enter()
        .append("g")
        .attr("class", "mouse-per-line");

      mousePerLine
        .append("circle")
        .attr("r", 7)
        .style("stroke", function(d) {
          return color(d.name);
        })
        .style("fill", "none")
        .style("stroke-width", "1px")
        .style("opacity", "0");

      mousePerLine.append("text").attr("transform", "translate(10,3)");

      mouseG
        .append("svg:rect") // append a rect to catch mouse movements on canvas
        .attr("width", width) // can't catch mouse events on a g element
        .attr("height", height)
        .attr("fill", "none")
        .attr("pointer-events", "all")
        .on("mouseout", function() {
          // on mouse out hide line, circles and text
          d3.select(".mouse-line").style("opacity", "0");
          d3.selectAll(".mouse-per-line circle").style("opacity", "0");
          d3.selectAll(".mouse-per-line text").style("opacity", "0");
        })
        .on("mouseover", function() {
          // on mouse in show line, circles and text
          d3.select(".mouse-line").style("opacity", "1");
          d3.selectAll(".mouse-per-line circle").style("opacity", "1");
          d3.selectAll(".mouse-per-line text").style("opacity", "1");
        })
        .on("mousemove", function() {
          // mouse moving over canvas
          var mouse = d3.mouse(this);
          d3.select(".mouse-line").attr("d", function() {
            var d = "M" + mouse[0] + "," + height;
            d += " " + mouse[0] + "," + 0;
            return d;
          });

          d3.selectAll(".mouse-per-line").attr("transform", function(d, i) {
            var xDate = x.invert(mouse[0]),
              bisect = d3.bisector(function(d) {
                return d.date;
              }).right;
            var idx = bisect(d.values, xDate);

            var beginning = 0,
              end = lines[i].getTotalLength(),
              target = null;

            while (true) {
              target = Math.floor((beginning + end) / 2);
              var pos = lines[i].getPointAtLength(target);
              if (
                (target === end || target === beginning) &&
                pos.x !== mouse[0]
              ) {
                break;
              }
              if (pos.x > mouse[0]) end = target;
              else if (pos.x < mouse[0]) beginning = target;
              else break; //position found
            }

            d3.select(this)
              .select("text")
              .text(y.invert(pos.y).toFixed(2));

            return "translate(" + mouse[0] + "," + pos.y + ")";
          });
        });
    },

    getForm() {
      const instruction =
        "Selecciona un campo fecha y uno o muchos campos numéricos";
      const name = "Gráfico cronológico";
      let fields = [];
      fields.push({
        name: "Fecha",
        type: [utils.date],
        model: "date",
        required: true,
        max: 1
      });
      fields.push({
        name: "Numéricos",
        type: [utils.number],
        model: "numerics",
        required: true,
        max: null
      });
      let form = {
        instruction,
        fields,
        name
      };
      return form;
    },

    // Processing
    transformData() {
      // process data
      let chartData = [];
      let dateColumn = this.columns.find(
        column => column.dataIndex == this.conf.date
      );
      this.rows.forEach(row => {
        let date = moment(row[dateColumn.dataIndex], dateColumn.format);
        if (String(date._d) !== "Invalid Date") {
          let chartItem = {
            date: date._d
          };
          this.conf.numerics.forEach(numeric => {
            chartItem[numeric] = utils.isNumeric(row[numeric])
              ? +row[numeric]
              : null;
          });
          chartData.push(chartItem);
        }
      });
      // end process data
      return chartData;
    },

    // API
    removeChart() {
      utils.removeChart(this);
    }
  }
};
</script>

<style>
.line {
  fill: none;
  stroke-width: 1px;
}

.axis path {
  stroke: black;
  stroke-width: 1px;
  fill: none;
  shape-rendering: crispEdges;
}

.tick line {
  stroke: black;
  stroke-width: 1px;
}
</style>