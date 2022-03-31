
// Global reference to Cytoscape graph - needed for `save_image`
var cy;

var hide_organisations = false;
var organisation_nodes;
var organisation_edges;

var anonymise_people = false;
var anonymise_organisations = false;

function nodeSize (ele) {
    return 100 + 20 * ele.connectedEdges().length;
}

var network_style = [
    {
        selector: 'node[name]',
        style: {
            label: function (ele) {
                var anonymise = anonymise_people;
                if (ele.data('kind') == 'organisation') {
                    anonymise = anonymise_organisations;
                }

                return anonymise ? ele.data('id') : ele.data('name')
            },
            width: nodeSize,
            height: nodeSize,
            textHalign: 'center',
            textValign: 'center',
            textWrap: 'wrap',
            textMaxWidth: function (ele) {
                return 0.8 * nodeSize(ele);
            },
            fontSize: function (ele) {
                return (16 + ele.connectedEdges().length).toString() + 'rem';
            },
            backgroundColor: 'data(nodeColor)',
            shape: 'data(nodeShape)',
            opacity: 0.7
        }
    },
    {
        selector: 'node:selected',
        style: {
            textMaxWidth: function (ele) {
                return 0.8 * nodeSize(ele);
            },
            fontSize: function (ele) {
                return (50 + ele.connectedEdges().length).toString() + 'rem';
            },
            zIndex: 100,
        }
    },
    {
        selector: 'edge',
        style: {
            midTargetArrowShape: 'data(lineArrowShape)',
            curveStyle: 'straight',
            width: 4,
            lineColor: 'data(lineColor)',
            opacity: 0.9
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
 * Hide or restore organisations and relationships with them.
 */
function toggle_organisations() {
    hide_organisations = !hide_organisations;

    if (hide_organisations) {
        organisation_nodes.remove();
        organisation_edges.remove();
    } else {
        organisation_nodes.restore();
        organisation_edges.restore();
    }
}

/**
 * Toggle person node labels between names and ids.
 */
function toggle_anonymise_people() {
    anonymise_people = !anonymise_people
    cy.elements().remove().restore();
}

/**
 * Toggle organisation node labels between names and ids.
 */
function toggle_anonymise_organisations() {
    anonymise_organisations = !anonymise_organisations
    cy.elements().remove().restore();
}

/**
 * Populate a Cytoscape network from :class:`Person` and :class:`Relationship` JSON embedded in page.
 */
function get_network() {
    // Initialise Cytoscape graph
    // See https://js.cytoscape.org/ for documentation
    cy = cytoscape({
        container: document.getElementById('cy'),
        style: network_style,
        wheelSensitivity: 0.2
    });

    // Add pan + zoom widget with cytoscape-panzoom
    cy.panzoom();

    // Load people and add to graph
    var person_set = JSON.parse(document.getElementById('person-set-data').textContent);

    for (var person of person_set) {
        cy.add({
            group: 'nodes',
            data: {
                id: 'person-' + person.pk.toString(),
                name: person.name,
                kind: 'person',
                nodeColor: '#0099cc',
                nodeShape: 'ellipse'
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
                kind: 'organisation',
                nodeColor: '#669933',
                nodeShape: 'rectangle'
            }
        })
    }
    organisation_nodes = cy.nodes('[kind = "organisation"]');

    // Load relationships and add to graph
    var relationship_set = JSON.parse(document.getElementById('relationship-set-data').textContent);

    for (var relationship of relationship_set) {
        try {
            cy.add({
                group: 'edges',
                data: {
                    id: 'relationship-' + relationship.pk.toString(),
                    source: 'person-' + relationship.source.pk.toString(),
                    target: 'person-' + relationship.target.pk.toString(),
                    kind: 'person',
                    lineColor: {
                        'organisation-membership': '#669933'
                    }[relationship.kind] || 'grey',
                    lineArrowShape: 'triangle'
                }
            })
        } catch (exc) {
            // Exception thrown if a node in the relationship does not exist
            // This is probably because it's been filtered out
        }
    }

    // Load organisation relationships and add to graph
    relationship_set = JSON.parse(document.getElementById('organisation-relationship-set-data').textContent);

    for (var relationship of relationship_set) {
        try {
            cy.add({
                group: 'edges',
                data: {
                    id: 'organisation-relationship-' + relationship.pk.toString(),
                    source: 'person-' + relationship.source.pk.toString(),
                    target: 'organisation-' + relationship.target.pk.toString(),
                    kind: 'organisation',
                    lineColor: {
                        'organisation-membership': '#669933'
                    }[relationship.kind] || 'black',
                    lineArrowShape: 'triangle'
                }
            })
        } catch (exc) {
            // Exception thrown if a node in the relationship does not exist
            // This is probably because it's been filtered out
        }
    }
    organisation_edges = cy.edges('[kind = "organisation"]');

    // Optimise graph layout
    var layout = cy.layout({
        name: 'cose',
        randomize: false,
        animate: false,
        nodeRepulsion: function (node) {
            return 2 ** node.connectedEdges().length;
        },
        nodeOverlap: 80
    });

    layout.run();

    setTimeout(function () {
        document.getElementById('cy').style.height = '100%';
    }, 1000)
}

$(window).on('load', get_network());
