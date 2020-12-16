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

let marker = null;

function selectLocation(event) {
    if (marker === null) {
        // Generate a new marker
        marker = new google.maps.Marker({
            position: event.latLng,
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
    } else {
        marker.setPosition(event.latLng);
    }

    const pos = marker.getPosition();
    console.log(pos.lat(), pos.lng());
    document.getElementById('id_latitude').value = pos.lat();
    document.getElementById('id_longitude').value = pos.lng();
}

// The function called when Google Maps starts up
function initMap() {
    const centre_latlng = new google.maps.LatLng(settings.centre_lat, settings.centre_lng);
    const map = new google.maps.Map(
        document.getElementById('map'), { zoom: settings.zoom, center: centre_latlng });

    google.maps.event.addListener(map, 'click', selectLocation)
}
