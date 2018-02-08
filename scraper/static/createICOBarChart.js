function createICOBarChart(margin, elem, current_bottom_table, top_ico_data) {
        
    var colorScale = d3.scaleOrdinal(d3.schemeCategory10);
    
    // set the ranges
    var x = d3.scaleBand()
            .range([0, margin.width]);

    var y = d3.scaleLinear()
            .range([margin.height, 0]);
                
    // append the svg object to the body of the page
    // append a 'group' element to 'svg'
    // moves the 'group' element to the top left margin
    var svg = d3.select(elem).append("svg")
        .attr("width", margin.width + margin.left + margin.right)
        .attr("height", margin.height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", 
            "translate(" + margin.left + "," + margin.top + ")");

        // get the data `(last_post, thread_id, subject, post_count)`
        d3.json("/top_icos", function(error, data) {
            if (error) throw error;
            
            data.top_icos.forEach(function(d) {
                d.post_count = +d.post_count;
                top_ico_data.push(d);
            });
            
            // Scale the range of the data in the domains
            x.padding(0.5)
                .domain(top_ico_data.map(d => d.subject));
            
            y.domain([0, d3.max(top_ico_data, function(d) { return d.post_count; })]);

            // append the rectangles for the bar chart
            bars = svg.selectAll(".bar")
                .data(top_ico_data)
                .enter().append("rect")
                .attr("class", "bar")
                .attr("x", function(d) { return x(d.subject); })
                .attr("width", x.bandwidth() )
                .attr("y", function(d) { return y(d.post_count); })
                .attr("height", function(d) { return margin.height - y(d.post_count); })
                .attr("fill", function(d) { return colorScale(d.post_count) });
               
            bars.on("click", function(bar) {
                d3.select("#bottom_table_container").select("table").remove();
                d3.json("/posts_by_thread/" + bar.thread_id, function(error, json) {
                    current_bottom_table.columns = json.columns;
                    current_bottom_table.rows = [];
                    json.rows.forEach(r => current_bottom_table.rows.push(r));
                });
                var table, thead, tbody, rows, cells = createTable(current_bottom_table, "bottom_table_container");
            });

            // add the x Axis
            svg.append("g")
                .attr("transform", "translate(0," + margin.height + ")")
                .call(d3.axisBottom(x))
                .selectAll(".tick text")
                    .call(wrap, x.bandwidth());

            // add the y Axis
            svg.append("g")
                .call(d3.axisLeft(y));
        });
    
    return svg, current_bottom_table, top_ico_data;
};