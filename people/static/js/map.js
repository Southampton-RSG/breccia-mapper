const marker_fill_alpha = 1.0;
const marker_edge_colour = 'white';
const marker_fill_colour =  'gray';

// Size of the arrow markers used on the map
const marker_scale = 9;
// Offset for the place type icon (multiplier for marker scale)
const marker_label_offset = 0.27 * marker_scale;
// Width and transparency for the edges of the markers
const marker_edge_alpha = 1.0;
const marker_edge_width = 1.0;

let map = null

// The function called when Google Maps starts up
function initMap() {
    // const centre_latlng = new google.maps.LatLng(settings.centre_lat, settings.centre_lng);
    // The map, centered at Soton
    map = new google.maps.Map(
        // document.getElementById('map'), { zoom: settings.zoom, center: centre_latlng });
        document.getElementById('map'));

    const bounds = new google.maps.LatLngBounds()
    const markers_data = JSON.parse(
        document.getElementById('map-markers').textContent
        ).filter(data => data.lat !== null && data.lng !== null);

    // For each data entry in the json...
    for (const pin_data of markers_data) {
        // Get the lat-long position from the data
        const lat_lng = new google.maps.LatLng(pin_data.lat, pin_data.lng);
        console.log(lat_lng)

        // Generate a new marker
        const marker = new google.maps.Marker({
            position: lat_lng,
            map: map,
            icon: {
                path: google.maps.SymbolPath.BACKWARD_CLOSED_ARROW,
                strokeColor: marker_edge_colour,
                strokeWeight: marker_edge_width,
                strokeOpacity: marker_edge_alpha,
                fillColor: marker_fill_colour,
                fillOpacity: marker_fill_alpha,
                scale: marker_scale,
                labelOrigin: new google.maps.Point(0, -marker_label_offset)
            },
        });

        console.log(marker)

        bounds.extend(marker.position)

        // Build the info window content to tell the user the last time it was visited.
        marker.info = new google.maps.InfoWindow({
            content: "<div id='content'>" +
                "<h3><a href=" + pin_data.url + ">" + pin_data.name.replace('&apos;', "'") + "</a></h3>" +
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

    map.fitBounds(bounds)
    const max_zoom = 10
    if (map.getZoom() > max_zoom) {
        map.setZoom(max_zoom)
    }


    // Set the last info window to null
    var last_info = null;

    setTimeout(setMaxZoom, 100)
}

/**
 * Zoom to set level if map is zoomed in more than this.
 */
function setMaxZoom() {
    const max_zoom = 10
    if (map.getZoom() > max_zoom) {
        map.setZoom(max_zoom)
    }
}
