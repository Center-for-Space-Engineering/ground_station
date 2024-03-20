// Define a global variable to store references to the Chart.js objects
var charts = {};

function open_tab(message) 
{
    // Call a Flask route using JavaScript
    if (message == 'Status Report')
    {
        window.location.href = '/';
    }
    else if (message == 'Data Stream')
    {
        window.location.href = '/open_data_stream';
    }
    else if (message == 'Sensor')
    {
        window.location.href = '/Sensor';

    } 
    else if (message == 'Command')
    {
        window.location.href = '/Command';

    }
}
function refresh_logger_report()
{
    // Fetch updated content list from Flask
    $.ajax({
        url: '/get_updated_logger_report',
        method: 'GET',
        success: function(data) {
            // Clear existing list items
            $('#logger_report').empty();

            // Parse and append updated content list
            data.logger_report.forEach(function(item) {
                $('#logger_report').append('<li class="white-text"><span class="green-text">Log:</span> [<span class="blue-text">' + item['time'] + '</span>] : ' + item['message'] + '</li>');
                // $('#logger_report').append('<li>' + 'Hello worlds' + '</li>');
            });
        },
        error: function(error) {
            // console.error('Error fetching logger updated content:', error);
        }
    });
}
function refresh_prem_logger_report()
{
    // Fetch updated content list from Flask
    $.ajax({
        url: '/get_updated_prem_logger_report',
        method: 'GET',
        success: function(data) {
            // Clear existing list items
            $('#prem_logger_report').empty();

            // Parse and append updated content list
            data.prem_logger_report.forEach(function(item) {
                $('#prem_logger_report').append('<li class="white-text"><span class="green-text">Log:</span> [<span class="blue-text">' + item['time'] + '</span>] : ' + item['message'] + '</li>');
            });
        },
        error: function(error) {
            // console.error('Error fetching logger updated content:', error);
        }
    });
}
function refresh_thread_report()
{
    // Fetch updated content list from Flask
    $.ajax({
        url: '/get_updated_thread_report',
        method: 'GET',
        success: function(data) {
            // Clear existing list items
            $('#thread_report').empty();

            // Parse and append updated content list
            data.thread_report.forEach(function(item) {
                if(item.status == "Running"){
                    $('#thread_report').append('<li class="white-text">[<span class="blue-text">' + item['time'] + '</span>] <span class="nice_teal">' + item['name'] + '</span>: <span class="green-text">' + item['message'] +'</span></li>');
                }
                else if (item.status == "Error"){
                    $('#thread_report').append('<li class="white-text">[<span class="red-text">' + item['time'] + '</span>] <span class="nice_teal">' + item['name'] + '</span>: <span class="red-text">' + item['message'] +'</span></li>');
                }
                else {
                    $('#thread_report').append('<li class="white-text">[<span class="blue-text">' + item['time'] + '</span>] <span class="nice_teal">' + item['name'] + '</span>: <span class="orange-text">' + item['message'] +'</span></li>');
                }
            });
        },
        error: function(error) {
            // console.error('Error fetching logger updated content:', error);
        }
    });
}
//This function updates our status report by sending a request to the server and then passing that response back to the webpage
function refresh_status_report()
{
    // Fetch updated content list from Flask
    $.ajax({
        url: '/get_refresh_status_report',
        method: 'GET',
        success: function(data) {
            // Clear existing list items
            $('#status_list').empty();

            // Parse and append updated content list
            data.status_list.forEach(function(item) {
                $('#status_list').append('<li class="white-text"><span class="nice_teal">' + item['name'] + '</span> Reported: <span class="orange-text">' + item['message'] + '</span></li>');
            });
            },
        error: function(error) {
            // console.error('Error fetching logger updated content:', error);
        }
    });
}
// Function to execute action based on what the user clicked on in the table
function update_run_arg_box(row) {
    //update the run commands text box
    var path_name = row.getAttribute('data-path');
    var input_command_box = document.getElementById('commands_args');
    input_command_box.value = path_name;
}
function downloadFileFromResponse(text, file, file_extension) {
    //creating an invisible element and download the file
    var element = document.createElement('a');
    element.setAttribute('href','data:text/plain;charset=utf-8;base64,' + text);
    element.setAttribute('download', file + "." + file_extension);
    document.body.appendChild(element);
    element.click();

    document.body.removeChild(element);
}
//This function takes an input from the user and then runs 
function send_run_request() {
    var userInput = document.getElementById('commands_args').value;
    document.getElementById('result').innerHTML = 'Running request...';


    fetch(`${userInput}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('result').innerHTML = data.text_data;
            if(data.download == 'yes') downloadFileFromResponse(data.file_data, 'data_download', data.file_extension);
        })
        .catch(error => {
            // console.error('Error making GET request:', error);
            document.getElementById('result').innerHTML = 'Error: ' + error.message;
        });
}
//This function takes an input from the user and then sends a command
function send_serial_request() {
    var userInput = document.getElementById('user_hex_input').value;
    var serial = document.getElementById('serial_writer_dropdown').value;
    

    // Define the data to be sent
    var data = {
        serial_command: userInput,
        serial_name: serial
    };

    // Convert the data object to a query string
    var queryString = Object.keys(data).map(key => key + '=' + data[key]).join('&');


    fetch(`/serial_run_request?` + queryString)
        .then(response => response.text())
        .then(data => {
            document.getElementById('result_serial').innerHTML = data;
        })
        .catch(error => {
            // console.error('Error making GET request:', error);
            document.getElementById('result_serial').innerHTML = 'Error: ' + error.message;
        });
}
//This function takes an input from the user and then sends a request
function send_serial_reconfig_request(type) {
    if (type == 'listener') {
        const dropdown = document.getElementById('serial_listener_dropdown');
        var requested_serial = dropdown.value; // Get the selected value
        var baud_rate = document.getElementById('baud_rate_listener').value;
        var stop_bit = document.getElementById('stop_bit_listener').value;
    }
    else
    {
        const dropdown = document.getElementById('serial_writer_dropdown');
        var requested_serial = dropdown.value; // Get the selected value
        var baud_rate = document.getElementById('baud_rate_writer').value;
        var stop_bit = document.getElementById('stop_bit_writer').value;
    }
    

    // Define the data to be sent
    var data = {
        baud_rate:baud_rate,
        stop_bit:stop_bit,
        requested:requested_serial
    };

    // Convert the data object to a query string
    var queryString = Object.keys(data).map(key => key + '=' + data[key]).join('&');


    fetch(`/start_serial?` + queryString)
        .then(response => response.text())
        .then(data => {
            if (type == 'listener') document.getElementById('result_serial_config_listener').innerHTML = data;
            else document.getElementById('result_serial_config_writer').innerHTML = data;
        })
        .catch(error => {
            // console.error('Error making GET request:', error);
            if (type == 'listener') document.getElementById('result_serial_config_listener').innerHTML = 'Error: ' + error.message;
            else document.getElementById('result_serial_config_writer').innerHTML = 'Error: ' + error.message;
        });
    //update the table
    update_serial_status();
}
function get_serial_listener_drop_down(){
    // Fetch data from the server
    fetch('/get_serial_names')
        .then(response => response.json()) // Assuming the server returns JSON data
        .then(data => {
            // Populate dropdown list with options for listener
            const dropdown = document.getElementById('serial_listener_dropdown');
            dropdown.innerHTML = ''; // Clear all existing options
            data.listener.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.textContent = option;
                dropdown.appendChild(optionElement);
            });
        })
        .catch();
}
function get_serial_writer_drop_down(){
    // Fetch data from the server
    fetch('/get_serial_names')
        .then(response => response.json()) // Assuming the server returns JSON data
        .then(data => {
            // Populate dropdown list with options for listener
            const dropdown = document.getElementById('serial_writer_dropdown');
            dropdown.innerHTML = ''; // Clear all existing options
            data.writer.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.textContent = option;
                dropdown .appendChild(optionElement);
            });
        })
        .catch();
}
// Function to fetch data from the server and update the table
function update_serial_status() {
    fetch('/get_serial_status')
        .then(response => response.json()) // Assuming the server returns JSON data
        .then(data => {
            const tableBody = document.getElementById('serial_status_body');
            tableBody.innerHTML = ''; // Clear existing rows
            data.forEach(item => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class = 'nice_teal'>${item.port}</td>
                    <td class = 'nice_teal'>${item.connected}</td>
                    <td class = 'nice_teal'>${item.buad_rate}</td>
                    <td class = 'nice_teal'>${item.stopbits}</td>
                    <td class = 'nice_teal'>${item.subscribers}</td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch();
}
// Function to update the graphs with the fetched data
function updateGraphs() {
    // const dropdown = document.getElementById('debug_box');
    fetch('/get_serial_info_update') 
        .then(response => response.json())
        .then(data => {
            updateCharts(data);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}
// Function to update chart data
function updateCharts(data) {
    // Iterate over each entry in the data
    data.forEach(function(entry) {
        // Iterate over each listener in the entry
        Object.keys(entry).forEach(function(listener) {
            // Check if the chart for this listener exists
            if (charts.hasOwnProperty(listener)) {
                // Get the chart object
                var chart = charts[listener];

                // Get the data for this listener
                var listenerData = entry[listener];

                // If the data length is greater than 10, slice it to get the last 10 entries
                if (listenerData.length > 10) {
                    listenerData = listenerData.slice(-10);
                }

                // Extract time and bytes data from listenerData
                var times = listenerData.map(function(entry) {
                    return entry.time;
                });
                var bytes = listenerData.map(function(entry) {
                    return entry.bytes;
                });

                // Update the chart data
                chart.data.labels = times;
                chart.data.datasets[0].data = bytes;

                // Update the chart
                chart.update();
            }
        });
    });
}
function makeGraphs(){
    // Fetch data from the server
    fetch('/get_serial_names')
        .then(response => response.json()) // Assuming the server returns JSON data
        .then(data => {
            data.listener.forEach(name => {
                // Create a new chart container div element
                var container = document.createElement('div');
                container.className = 'box_style'; // Apply the .box_style class
                document.getElementById('graphs').appendChild(container);

                // Create a canvas element for the graph
                var canvas = document.createElement('canvas');
                canvas.width = 200; // Set width
                canvas.height = 150; // Set height
                canvas.id = 'graph-' + name; // Set unique id for each graph

                container.appendChild(canvas);
        
                // Get the context of the canvas
                var ctx = canvas.getContext('2d');
        
                // Create a new chart with an empty dataset and the name as label
                charts[name] = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: [], // No data, just labels
                        datasets: [{
                            label: name,
                            data: [],
                            fill: false,
                            borderColor: 'rgb(75, 192, 192)',
                            tension: 0.1
                        }]
                    },
                    options: {
                        scales: {
                            yAxes: [{
                                ticks: {
                                    beginAtZero: true
                                }
                            }]
                        }
                    }
                });
            })
        })
        .catch();
}
// Function to fetch data from the server and update the table
function update_sensor_status() {
    fetch('/get_sensor_status ')
        .then(response => response.json()) // Assuming the server returns JSON data
        .then(data => {
            const tableBody = document.getElementById('sensors_status_report');
            tableBody.innerHTML = ''; // Clear existing rows
            data.forEach(item => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class = 'nice_teal'>${item.name}</td>
                    <td class = 'nice_teal'>${item.status}</td>
                    <td class = 'nice_teal'>${item.taps}</td>
                `;
                row.addEventListener('click', function() {
                    open_sensor_page(item.name) });
                tableBody.appendChild(row);
            });
        })
        .catch();
}

function open_sensor_page(name) 
{
    // Define the data to be sent
    var data = {
        name : name,
    };

    // Convert the data object to a query string
    var queryString = Object.keys(data).map(key => key + '=' + data[key]).join('&');

    // Open new webpage
    window.location.href = `/sensor_page?` + queryString;
}