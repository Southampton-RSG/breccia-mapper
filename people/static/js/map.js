const marker_main_alpha_never = 1.0;
const marker_main_alpha_future = 1.0;
const marker_main_alpha = 1.0;

const marker_main_colour_never = 'grey';
const marker_main_colour_future = 'white';

const marker_edge_colour = 'white';
const marker_edge_colour_never = 'white';
const marker_edge_colour_future = 'black';


// Size of the arrow markers used on the map
const marker_scale = 9;
// Offset for the place type icon (multiplier for marker scale)
const marker_label_offset = 0.27 * marker_scale;
// Width and transparency for the edges of the markers
const marker_edge_alpha = 1.0;
const marker_edge_width = 1.0;

const settings = {
    zoom: 5
}

// const data = [
//     {lat: 0, lng: 0, name: 'a'},
//     {lat: 1, lng: 1, name: 'b'},
//     {lat: 2, lng: 2, name: 'c'},
// ]



// Pull settings from the settings var
// const time_after = filters.time_after;
// const time_before = filters.time_before;
// Set up a colour scale that goes from blue to red via yellow, over time_limit days
// const visitedColour = d3.scaleSequential(d3.interpolateRdYlBu)
//     .domain([filters.time_after, filters.time_before]);


// The function called when Google Maps starts up
function initMap() {
    const centre_latlng = new google.maps.LatLng(0, 0);
    // The map, centered at Soton
    const map = new google.maps.Map(
        document.getElementById('map'), { zoom: settings.zoom, center: centre_latlng });

    // For each data entry in the json...
    for (var i = 0; i < data.length; i++) {
        // Get the lat-long position from the data
        var lat_lng = new google.maps.LatLng(data[i].lat, data[i].lng);

        // Generate a new marker
        var marker = new google.maps.Marker({
            position: lat_lng, map: map,
            icon: {
                path: google.maps.SymbolPath.BACKWARD_CLOSED_ARROW,
                strokeColor: edgeColourByTime(data[i]),
                strokeWeight: marker_edge_width,
                strokeOpacity: marker_edge_alpha,
                fillColor: mainColourByTime(data[i]),
                fillOpacity: alphaByTime(data[i]),
                scale: marker_scale,
                labelOrigin: new google.maps.Point(0, -marker_label_offset)
            },
            label: (data[i].type === 'school' ? '🎓' : '')
        });

        // Build the info window content to tell the user the last time it was visited.
        marker.info = new google.maps.InfoWindow({
            content: "<div id='content'>" +
                "<h3><a href=" + data[i].url + ">" + data[i].name.replace('&apos;', "'") + "</a></h3>" +
                (data[i].hasOwnProperty('lastvisit') ? "<p>Last visited " + data[i].lastvisit + "</p>" : "<p>Never visited</p>") +
                "</div>"
        });

        // We bind a listener to the current marker so that if it's clicked, it checks for an open info window,
        // closes it, then opens the info window attached to it specifically. Then sets that as the last window.
        google.maps.event.addListener(marker, 'click', function () {
            if (last_info) {
                last_info.close();
            }
            last_info = this.info;
            this.info.open(map, this);
        })
    }

    // Set the last info window to null
    var last_info = null;
}


function mainColourByTime(d) {
    if (!d.hasOwnProperty('time')) {
        return marker_main_colour_never;
    } else if (d.time > time_after) {
        return visitedColour(time_after);
    } else if (d.time < time_before) {
        return marker_main_colour_future;
    } else {
        return visitedColour(d.time);
    }
}

function edgeColourByTime(d) {
    if (!d.hasOwnProperty('time')) {
        return marker_edge_colour_never;
    } else if (d.time > time_after) {
        return marker_edge_colour;
    } else if (d.time < time_before) {
        return marker_edge_colour_future;
    } else {
        return marker_edge_colour;
    }
}

function alphaByTime(d) {
    if (!d.hasOwnProperty('time')) {
        return marker_main_alpha_never;
    } else if (d.time > time_after) {
        return marker_main_alpha;
    } else if (d.time < time_before) {
        return marker_main_alpha_future;
    } else {
        return marker_main_alpha;
    }
}
