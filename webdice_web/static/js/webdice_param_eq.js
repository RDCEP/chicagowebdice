
  var advanced_equations = {
    temp_co2_doubling: {
      width: 230,
      max: 'max',
      scale: 'linear',
      legend: 'Forcings v. Temp',
      output: function (v) {
        var output = [];
        for (var i = 0; i < 10; ++i) {
          output.push({
            y: 0.7307 + 0.22 * ((i + 1) - (3.8 / v) * 0.7307 - 0.3 * (0.7307 - 0.0068)),
            x: i + 1
          });
        }
        return output;
      }
    },
    damages_exponent: {
      width: 230,
      max: 'max',
      scale: 'linear',
      legend: 'Damages v. Temp',
      output: function (v) {
        var output = [];
        for (var i = 0; i < 10; ++i) {
          var y = 1 - 1 / (1 + 0.0028388 * Math.pow(i, v));
          output.push({
            y: y,
            x: i + 1
          });
        }
        return output;
      }
    },
    productivity_decline: {
      width: 158,
      max: 'min',
      scale: 'linear',
      legend: 'Productivity v. Time',
      output: function (v) {
        var output = [{y: 0.0303, x: 1}];
        for (var i = 1; i < 10; ++i) {
          var y = output[i - 1].y / (1 - 0.16 * Math.exp(-v / 100 * i * 10 ));
          output.push({
            y: y,
            x: i + 1
          });
        }
        return output;
      }
    },
    popasym: {
      width: 158,
      max: 'max',
      scale: 'linear',
      legend: 'Population v. Time',
      output: function (v) {
        var o = [];
        for (var i = 0; i < 10; ++i) {
          var y = 6514 * (1 - (Math.exp(.35 * i) - 1) / Math.exp(.35 * i)) + (Math.exp(.35 * i) - 1) / Math.exp(.35 * i) * v;
          o.push({
            y: y,
            x: i + 1
          });
        }
        return o;
      }
    },
    abatement_exponent: {
      width: 230,
      max: 'max',
      scale: 'linear',
      legend: 'Abatement costs v. Time',
      output: function (v) {
        var o = [];
        for (var i = 0; i < 10; ++i) {
          var y = Math.pow(i, v);
          o.push({
            y: y,
            x: i + 1
          });
        }
        return o;
      }
    },
    backstop_decline: {
      width: 230,
      max: 'max',
      scale: 'linear',
      legend: 'Clean Energy Cost v. Time',
      output: function (v) {
        var o = [{y: 0.344, x: 1}];
        for (var i = 1; i < 10; ++i) {
          var y = o[i - 1].y * (1 - v / 100);
          o.push({
            y: y,
            x: i + 1
          });
        }
        return o;
      }
    },
    intensity_decline_rate: {
      width: 230,
      max: 'min',
      scale: 'linear',
      legend: 'Carbon intensity decline v. Time',
      output: function (v) {
        var o = [],
          p = 0.13418;
        for (var i = 0; i < 10; ++i) {
          var d = -0.073 * Math.exp(-v/100 * 10 * i),
            y = p / (1 - d);
          o.push({
            y: y,
            x: i + 1
          });
          p = y;
        }
        return o;
      }
    }
  },

  standard_equations = {
    temp_co2_doubling: {
      width: 230,
      max: 'max',
      scale: 'linear',
      legend: 'Forcings v. Temp',
      output: function (v) {
        v = [1,2,3.2,4,5][v - 1];
        var output = [];
        for (var i = 0; i < 10; ++i) {
          output.push({
            y: 0.7307 + 0.22 * ((i + 1) - (3.8 / v) * 0.7307 - 0.3 * (0.7307 - 0.0068)),
            x: i + 1
          });
        }
        return output;
      }
    },
    damages_exponent: {
      width: 230,
      max: 'max',
      scale: 'linear',
      legend: 'Damages v. Temp',
      output: function (v) {
        v = [1, 1.4, 2.0, 2.8, 4.0][v - 1];
        var output = [];
        for (var i = 0; i < 10; ++i) {
          var y = 1 - 1 / (1 + 0.0028388 * Math.pow(i, v));
          output.push({
            y: y,
            x: i + 1
          });
        }
        return output;
      }
    },
    productivity_decline: {
      width: 230,
      max: 'max',
      scale: 'log',
      legend: 'Productivity v. Time',
      output: function (v) {
        v = [.015, .011, .009, .003, 0.0][v - 1];
        var p = [.02722],
          output = [{y: p[0], x: 1}];
        for (var i = 1; i < 10; ++i) {
          var y = p[i - 1] / (1 - 0.092 * Math.exp(-v * 10 * i));
          p.push(y);
          output.push({
            y: y,
            x: i + 1
          });
        }
        return output;
      }
    },
    backstop_ratio: {
      width: 230,
      max: 'max',
      scale: 'linear',
      legend: 'Clean Energy Cost v. Time',
      output: function (v) {
        v = [1, 1.4, 2.0, 2.8, 4.0][v - 1];
        var o = [];
        for (var i = 0; i < 10; ++i) {
          var y = 1.17 * (v - 1 + Math.exp(-5/100 * i)) / v * 12 / 44;
          o.push({
            y: y,
            x: i + 1
          });
        }
        return o;
      }
    },
    intensity_decline_rate: {
      width: 230,
      max: 'max',
      scale: 'linear',
      legend: 'Carbon intensity decline v. Time',
      output: function (v) {
        v = [6.0, 2., 0.65, 0.06, 0.0][v - 1];
        var o = [],
          p = 0.13418;
        for (var i = 0; i < 10; ++i) {
          var d = -0.073 * Math.exp(-v/100 * 10 * i),
            y = p / (1 - d);
          o.push({
            y: y,
            x: i + 1
          });
          p = y;
        }
        return o;
      }
    }
  };