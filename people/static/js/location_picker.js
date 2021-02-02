
let search_markers = []

/**
 * Position a map marker at the clicked location and update lat/long form fields.
 * @param {Event} event - Click event from a Google Map.
 */
function selectLocation(event) {
    if (selected_marker === null) {
        // Generate a new marker
        selected_marker = new google.maps.Marker({
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
        selected_marker.setPosition(event.latLng);
    }

    const pos = selected_marker.getPosition();
    document.getElementById('id_latitude').value = pos.lat();
    document.getElementById('id_longitude').value = pos.lng();
}

function displaySearchResults() {
    const places = search_box.getPlaces()

    if (places.length === 0) return

    for (const marker of markers) marker.setMap(null)
    search_markers = []

    const bounds = new google.maps.LatLngBounds()
    for (const place of places) {
        if (!place.geometry) {
            console.error('Place contains no geometry')
            continue
        }

        const icon = {
            size: new google.maps.Size(71, 71),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(17, 34),
            scaledSize: new google.maps.Size(25, 25),
        }

        search_markers.push(
            new google.maps.Marker({
                map, icon, title: place.name, position: place.geometry.location
            })
        )

        if (place.geometry.viewport) {
            bounds.union(place.geometry.viewport)
        } else {
            bounds.extend(place.geometry.location)
        }

    }

    map.fitBounds(bounds)
}

/**
 * Initialise Google Maps element as a location picker.
 */
function initPicker() {
    map = initMap()

    const search_input = document.getElementById('location-search')
    const search_box = new google.maps.places.SearchBox(search_input)
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(search_input)

    map.addListener('bounds_changed', () => {
        search_box.setBounds(map.getBounds())
    })

    search_box.addListener('places_changed', displaySearchResults)

    map.addListener('click', selectLocation)
}
