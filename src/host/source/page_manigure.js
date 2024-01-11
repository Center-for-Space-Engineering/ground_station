function open_tab(message) {
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
