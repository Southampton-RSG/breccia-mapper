
// Global reference to Cytoscape graph - needed for `save_image`
var cy;

var network_style = [
    {
        selector: 'node[name]',
        style: {
            label: 'data(name)',
            'text-halign': 'center',
            'text-valign': 'center',
            'font-size': 8,
            'background-color': function (ele) {
                switch (ele.data('kind')) {
                    case 'person':
                        return '#0099cc'
                    default:
                        return '#669933'
                }
            },
            'shape': function (ele) {
                switch (ele.data('kind')) {
                    case 'person':
                        return 'ellipse'
                    default:
                        return 'rectangle'
                }
            }
        }
    },
    {
        selector: 'edge',
        style: {
            'mid-target-arrow-shape': 'triangle',
            'curve-style': 'straight',
            'width': 1,
        }
    }
]

/**
 * Save the network as an image using the browser's normal file download flow.
 */
function save_image() {
    saveAs(cy.png(), 'graph.png');
}

/**
 * Populate a Cytoscape network from :class:`Person` and :class:`Relationship` JSON embedded in page.
 */
function get_network() {
    // Initialise Cytoscape graph
    // See https://js.cytoscape.org/ for documentation
    cy = cytoscape({
        container: document.getElementById('cy'),
        style: network_style
    });

    // Load people and add to graph
    var person_set = JSON.parse(document.getElementById('person-set-data').textContent);

    for (var person of person_set) {
        cy.add({
            group: 'nodes',
            data: {
                id: 'person-' + person.pk.toString(),
                name: person.name,
                kind: 'person'
            }
        })
    }

    // Load organisations and add to graph
    var organisation_set = JSON.parse(document.getElementById('organisation-set-data').textContent);

    for (var item of organisation_set) {
        cy.add({
            group: 'nodes',
            data: {
                id: 'organisation-' + item.pk.toString(),
                name: item.name,
                kind: 'organisation'
            }
        })
    }

    // Load relationships and add to graph
    var relationship_set = JSON.parse(document.getElementById('relationship-set-data').textContent);

    for (var relationship of relationship_set) {
        try {
            cy.add({
                group: 'edges',
                data: {
                    id: 'relationship-' + relationship.pk.toString(),
                    source: 'person-' + relationship.source.pk.toString(),
                    target: 'person-' + relationship.target.pk.toString()
                }
            })
        } catch {
            // Exception thrown if a node in the relationship does not exist
            // This is probably because it's been filtered out
        }
    }

    // Load organisation relationships and add to graph
    relationship_set = JSON.parse(document.getElementById('organisation-relationship-set-data').textContent);

    for (var relationship of relationship_set) {
        console.log(relationship)
        try {
            cy.add({
                group: 'edges',
                data: {
                    id: 'organisation-relationship-' + relationship.pk.toString(),
                    source: 'person-' + relationship.source.pk.toString(),
                    target: 'organisation-' + relationship.target.pk.toString()
                }
            })
        } catch {
            // Exception thrown if a node in the relationship does not exist
            // This is probably because it's been filtered out
        }
    }

    // Optimise graph layout
    var layout = cy.layout({
        name: 'cose',
        randomize: true,
        animate: false,
        idealEdgeLength: function (edge) { return 64; }
    });

    layout.run();
}

$(window).on('load', get_network());
