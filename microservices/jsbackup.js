<script>
    var socket = new WebSocket('ws://' + window.location.host + '/ws/stock/')
    socket.addEventListener('open', function (event) {
        console.log('WebSocket connection opened');
    });

    // Listen for messages
    socket.addEventListener('message', function (event) {
        var data = JSON.parse(event.data);
        var message = data['message'];
        // Handle the received message, e.g., update UI
        console.log('Received message: ', message);
    });

    // Connection closed
    socket.addEventListener('close', function (event) {
        console.log('WebSocket connection closed');
    });
    document.addEventListener('DOMContentLoaded', function () {
        var rowData = [];

        // Populate rowData with your data
        {% for key, value in message.items %}
            var change =  parseFloat('{{ value.Previous_Close }}') - parseFloat('{{ value.Quote_Price }}');
            rowData.push({
                'SNo': '{{ key }}',
                'MarketCap': '{{ value.Market_Cap }}',
                'QuotePrice': '{{ value.Quote_Price }}',
                'PreviousClose': '{{ value.Previous_Close }}',
                'Volume': '{{ value.Volume }}',
                'Change': change
            });
        {% endfor %}

        // specify the columns
        var columnDefs = [
            { headerName: 'SNo', field: 'SNo' },
            { headerName: 'MarketCap', field: 'MarketCap' },
            { headerName: 'Previous Close', field: 'PreviousClose' },
            { headerName: 'Quote Price', field: 'QuotePrice' },
            { headerName: 'Change', field: 'Change',
              cellStyle: function(params) {
                return params.value < 0 ? {color: 'red'} : {color: 'green'};
              }
            },
            { headerName: 'Volume', field: 'Volume' },
            

        ];

        // let the grid know which columns to use
        var gridOptions = {
            columnDefs: columnDefs,
            rowData: rowData
        };

        // lookup the container we want the Grid to use
        var eGridDiv = document.querySelector('#agGrid');

        // create the grid passing in the div to use together with the columns & data we want to use
        agGrid.createGrid(eGridDiv, gridOptions);
    });
</script>