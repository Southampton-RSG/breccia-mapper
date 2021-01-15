const marker_fill_alpha = 1.0;
const marker_edge_colour = 'white';
const marker_fill_colour = 'gray';

// Size of the arrow markers used on the map
const marker_scale = 9;
// Offset for the place type icon (multiplier for marker scale)
const marker_label_offset = 0.27 * marker_scale;
// Width and transparency for the edges of the markers
const marker_edge_alpha = 1.0;
const marker_edge_width = 1.0;

let map = null;
let selected_marker_info = null;

function createMarker(map, marker_data) {
    // Get the lat-long position from the data
    const lat_lng = new google.maps.LatLng(marker_data.lat, marker_data.lng);

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

    marker.info = new google.maps.InfoWindow({
        content: "<div id='content'>" +
            "<h3><a href=" + marker_data.url + ">" + marker_data.name.replace('&apos;', "'") + "</a></h3>" +
            "</div>"
    });

    // We bind a listener to the current marker so that if it's clicked, it checks for an open info window,
    // closes it, then opens the info window attached to it specifically. Then sets that as the last window.
    google.maps.event.addListener(marker, 'click', function () {
        if (selected_marker_info) {
            selected_marker_info.close();
        }

        selected_marker_info = this.info;
        this.info.open(map, this);
    })

    return marker;
}

function search_missing_locations(map, markers_data) {
    service = new google.maps.places.PlacesService(map)

    for (let data of markers_data) {
        if (data.organisation !== null && (data.lat === null || data.lng === null)) {
            let query = data.organisation;
            if (data.country !== null) {
                query += ' ' + data.country;
            }

            const request = {
                query: query,
                fields: ['name', 'geometry'],
            };

            service.findPlaceFromQuery(request, (results, status) => {
                if (status === google.maps.places.PlacesServiceStatus.OK) {
                    for (let i = 0; i < results.length; i++) {
                        // createMarker(results[i]);
                        console.log(results[i])
                    }
                    map.setCenter(results[0].geometry.location);
                }
            });

            break;
        }
    }
}

// The function called when Google Maps starts up
function initMap() {
    map = new google.maps.Map(
        // document.getElementById('map'), { zoom: settings.zoom, center: centre_latlng });
        document.getElementById('map'));

    const bounds = new google.maps.LatLngBounds()
    const markers_data = JSON.parse(
        document.getElementById('map-markers').textContent)
    search_missing_locations(map, markers_data);

    // For each data entry in the json...
    for (const marker_data of markers_data) {
        const marker = createMarker(map, marker_data);
        bounds.extend(marker.position)
    }

    map.fitBounds(bounds)
    const max_zoom = 10
    if (map.getZoom() > max_zoom) {
        map.setZoom(max_zoom)
    }

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
