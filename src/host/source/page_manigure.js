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
    //If the data is bin data then it needs to be decoded
    if(file_extension == 'bin'){
        // Decode the base64 string
        text = atob(text);
    }

    //creating an invisible element and download the file
    var element = document.createElement('a');
    element.setAttribute('href','data:text/plain;charset=utf-8' + text);
    element.setAttribute('download', file + "." + file_extension);
    document.body.appendChild(element);
    element.click();

    document.body.removeChild(element);
}

//This function takes an input from the user and then runs 
function send_run_request() {
    var userInput = document.getElementById('commands_args').value;

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

    // Define the data to be sent
    var data = {
        serial_command: userInput
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
function send_serial_reconfig_request() {
    var baud_rate = document.getElementById('baud_rate').value;
    var stop_bit = document.getElementById('stop_bit').value;

    // Define the data to be sent
    var data = {
        baud_rate:baud_rate,
        stop_bit: stop_bit
    };

    // Convert the data object to a query string
    var queryString = Object.keys(data).map(key => key + '=' + data[key]).join('&');


    fetch(`/start_serial?` + queryString)
        .then(response => response.text())
        .then(data => {
            document.getElementById('result_serial_config').innerHTML = data;
        })
        .catch(error => {
            // console.error('Error making GET request:', error);
            document.getElementById('result_serial_config').innerHTML = 'Error: ' + error.message;
        });
}