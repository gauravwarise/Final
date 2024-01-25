
  document.addEventListener('DOMContentLoaded', function () {
    var dataFromBackend = {{ data }};

  // Transform the data into an array of objects
  var rowData = Object.keys(dataFromBackend).map(function (key) {
    return { 'symbol': key, ...dataFromBackend[key] };
  });

  // Column definitions
  var columnDefs = Object.keys(rowData[0]).map(function (key) {
    return {
      headerName: key,
      field: key
    };
  });

  // Grid options
  var gridOptions = {
    columnDefs: columnDefs,
    rowData: rowData,
    domLayout: 'autoHeight',
    defaultColDef: {
      resizable: true
    },
    animateRows: true
  };

  // Create the grid
  var gridDiv = document.querySelector('#ag-grid');
  new agGrid.Grid(gridDiv, gridOptions);
});