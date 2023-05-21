function draw_chart(index, name, labels, datasets) {
    var ctx = $('#canvas_' + index);
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: name
                }
            },
            responsive: true,
        }
    });
}

function getRandomColor() {
    var r = Math.floor(Math.random() * 256);
    var g = Math.floor(Math.random() * 256);
    var b = Math.floor(Math.random() * 256);
    return `rgb(${r}, ${g}, ${b})`;
}

function get_data(chartIndex, monitor) {
    var now = new Date();
    var twentyFourHoursAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    var isoString = twentyFourHoursAgo.toISOString();
    $.ajax({
        url: mainApi + '?scrape=' + monitor.name + '&datetime_after=' + isoString,
        type: 'GET',
        success: function (response) {
            var data_list = response;
            var labels = [];
            var datasets = {};
            monitor.scrape_fields.forEach(function (field){
                datasets[field]= {
                    label: field, data: [], borderColor: getRandomColor(),
                    pointRadius: 0, tension: 0.1};
            })
            data_list.forEach(function (data) {
                var datetime = new Date(data.datetime);
                var formattedTime = datetime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                labels.push(formattedTime);
                $.each(data.data, function(key, value){
                    datasets[key].data.push(value);
                });
            });
            draw_chart(chartIndex, monitor.name, labels, Object.values(datasets));
        },
        error: function (xhr, status, error) {
        }
    });
}

$(document).ready(function() {
    monitor_list.forEach(function(monitor){
        if (currentChartIndex < maxChart){
            get_data(currentChartIndex, monitor);
            currentChartIndex ++;
        }
    })
});
