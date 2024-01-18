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
            console.error('Error fetching logger updated content:', error);
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
            console.error('Error fetching logger updated content:', error);
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
            console.error('Error fetching logger updated content:', error);
        }
    });
}