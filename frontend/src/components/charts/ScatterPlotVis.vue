<template>
  <div>
    <a-row>
      <a-col :span="3">
        <a-button
          style="float: left; margin-bottom: 50px"
          type="primary"
          @click="removeChart()"
        >Eliminar Grafico</a-button>
      </a-col>
      <a-col :span="21">
        <div ref="chart" />
      </a-col>
    </a-row>
  </div>
</template>

<script>
import * as d3 from "d3";
import types from "@/utils/types";
import rendering from "@/utils/rendering";
import { Row, Col, Button } from "ant-design-vue";

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
    "a-row": Row,
    "a-col": Col,
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
    draw(data) {
      // set the dimensios and margins of the graph
      let margin = { top: 10, right: 30, bottom: 200, left: 200 },
        width = 800 - margin.left - margin.right,
        height = 600 - margin.top - margin.bottom;

      // append the svg object to the body of the page
      var svg = d3
        .select(this.$refs.chart)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      let xType = this.columns.find(
        column => column.dataIndex == this.conf.ejex
      ).type;
      let yType = this.columns.find(
        column => column.dataIndex == this.conf.ejey
      ).type;

      let xValues = data.map(element => element.x);
      let yValues = data.map(element => element.y);
      let x, y;

      if (xType == utils.number) {
        // Add Y axis
        let domainXTo = Math.max(...xValues);
        x = d3.scale
          .linear()
          .domain([domainXTo, 0])
          .range([height, 0]);
        svg
          .append("g")
          .attr("transform", "translate(0," + height + ")")
          .call(
            d3.svg
              .axis()
              .scale(x)
              .orient("bottom")
          );
      } else {
        // Add X axis
        x = d3.scale
          .ordinal()
          .domain(xValues)
          .rangePoints([0, width]);
        svg
          .append("g")
          .attr("transform", "translate(0," + height + ")")
          .call(
            d3.svg
              .axis()
              .scale(x)
              .orient("bottom")
          )
          .selectAll("text")
          .style("text-anchor", "end")
          .attr("dx", "-.8em")
          .attr("dy", ".15em")
          .attr("transform", function(d) {
            return "rotate(-90)";
          });
      }

      if (yType == utils.number) {
        // Add Y axis
        let domainYTo = Math.max(...yValues);
        y = d3.scale
          .linear()
          .domain([0, domainYTo])
          .range([height, 0]);
        svg.append("g").call(
          d3.svg
            .axis()
            .scale(y)
            .orient("left")
        );
      } else {
        // Add Y axis
        y = d3.scale
          .ordinal()
          .domain(yValues)
          .rangePoints([height, 0]);
        svg.append("g").call(
          d3.svg
            .axis()
            .scale(y)
            .orient("left")
        );
      }

      // Define the div for the tooltip
      var div = d3
        .select("body")
        .append("div")
        .style("position", "absolute")
        .style("text-align", "center")
        .style("width", "100px")
        .style("height", "80px")
        .style("padding", "5px")
        .style("overflow", "hidden")
        .style("font", "12px sans-serif")
        .style("background-color", "#d1e8e3")
        .style("border", "0px")
        .style("color", "black")
        .style("font-weight", "bold")
        .style("border-radius", "8px")
        .style("pointer-events", "none")
        .style("opacity", 0);

      // Add dots
      svg
        .append("g")
        .selectAll("dot")
        .data(data)
        .enter()
        .append("circle")
        .attr("cx", function(d) {
          return x(d.x);
        })
        .attr("cy", function(d) {
          return y(d.y);
        })
        .attr("r", 7)
        .style("fill", "#69b3a2")
        .style("opacity", 0.3)
        .style("stroke", "white")
        .on("mouseover", function(d) {
          div
            .transition()
            .duration(200)
            .style("opacity", 0.9);
          div
            .html(`x: ${d.x} <br> y: ${d.y}`)
            .style("left", d3.event.pageX + "px")
            .style("top", d3.event.pageY - 28 + "px");
        })
        .on("mouseout", function(d) {
          div
            .transition()
            .duration(500)
            .style("opacity", 0);
        });
    },

    getForm() {
      const instruction = "Selecciona un eje x y un eje y";
      const name = "Gráfico de dispersión";
      let fields = [];
      fields.push({
        name: "Eje x",
        type: [],
        model: "ejex",
        required: true,
        max: 1
      });
      fields.push({
        name: "Eje y",
        type: [],
        model: "ejey",
        required: true,
        max: 1
      });
      let form = {
        instruction,
        fields,
        name
      };
      return form;
    },

    // Processing data
    transformData() {
      let chartData = [];
      this.rows.forEach(row => {
        let xType = this.columns.find(
          column => column.dataIndex == this.conf.ejex
        ).type;
        let yType = this.columns.find(
          column => column.dataIndex == this.conf.ejey
        ).type;
        let xValue = row[this.conf.ejex];
        let yValue = row[this.conf.ejey];
        // check eje x
        if (
          (xType === utils.number && utils.isNumeric(xValue)) ||
          xType !== utils.number
        ) {
          // check eje y
          if (
            (yType === utils.number && utils.isNumeric(yValue)) ||
            yType !== utils.number
          ) {
            let chartElement = {
              x: xValue,
              y: yValue
            };
            chartData.push(chartElement);
          }
        }
      });
      return chartData;
    },

    // API
    removeChart() {
      utils.removeChart(this);
    }
  }
};
</script>