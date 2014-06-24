function basic_tab(data) {
  var new_values = {
    'temp_co2_doubling': [1,2,3.2,4,5],
    'damages_exponent': [1, 1.4, 2.0, 2.8, 4.0],
    'productivity_decline': [.015, .011, .009, .003, 0.0],
    'intensity_decline_rate': [.060, .02, .0065, .0006, 0.0],
    'backstop_ratio': [1, 1.4, 2.0, 2.8, 4.0]
    }
  ;
  data = data.slice(0,data.search('temp_co2_doubling'));
  $('#tab-beliefs').find('input').each(function() {
    $(this).val(function(i, v) {
      data += '&' + $(this).attr('name') + '=';
      data += new_values[$(this).attr('name')][v-1];
      return v;
    });
  });
  return data;
}