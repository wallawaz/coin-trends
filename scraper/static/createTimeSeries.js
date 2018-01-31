function createBBTimeSeries(elem, data_array) {
    console.log(data_array[0]);
    var chart = bb.generate({
        data: {
            x: "x",
            columns: data_array
        },
        axis: {
            x: {
                type: "timeseries",
                tick : {
                    format: "%Y-%m-%d %H:00:00"
                }
            }
        },
        bindto: elem
    });
    return chart;
}