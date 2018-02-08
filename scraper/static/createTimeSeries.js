function createBBTimeSeries(hours, elem, data_array) {

    /* make `hours_back` dynamic */
    let timeSeriesChart = $.ajax({
        url: "/coin_summary_by_hour/" + hours,
        type: "GET",
        dataType: "json",
        success: function(data) {
        },
        error: function(req, error) {
            console.log("error: " + JSON.stringify(error));
        }
    }).then(function(data) {
        data_array.length = 0;
        data_array.push(data.hours);
        data.records.forEach(r => data_array.push(r));
        const tsChart = bb.generate({
            data: {
                x: "x",
                columns: data_array,
                xFormat: "%Y-%m-%d %H:%M:%S"
            },
            axis: {
                x: {
                    type: "timeseries",
                    tick : {
                       format: "%Y-%m-%d %H:%M:%S"
                    }
                }
            },
            bindto: elem
        })
    });
    return timeSeriesChart, data_array;
}