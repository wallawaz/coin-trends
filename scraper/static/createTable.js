function createTable(data, elem_id) {
    const columns = data.columns;
    const container = "#" + elem_id;
    console.log(container);

    var table = d3.select(container).append("table"),
        thead = table.append("thead"),
        tbody = table.append("tbody");

    // append the header row
    thead.append("tr")
        .selectAll("th")
        .data(columns)
        .enter()
        .append("th")
        .text(function (column) { return column; });

    // create a row for each object in the data
    var rows = tbody.selectAll("tr")
        .data(data.rows)
        .enter()
        .append("tr");

    // create a cell in each row for each column
    var cells = rows.selectAll("td")
        .data(function (row) {
            return columns.map(function (column) {
                return { column: column, value: row[column] };
            });
        })
        .enter()
        .append("td")
        .text(function (d) { return d.value; }
        )

    return [table, thead, tbody, rows, cells];
}