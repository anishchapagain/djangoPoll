/**
 * Created by PETERCHAPAGAIN on 2/14/2017.
 */
$(document).ready(function() {
	$(chart_id).highcharts({
		chart: chart,
		title: title,
		xAxis: xAxis,
		yAxis: yAxis,
		series: series
	});
});