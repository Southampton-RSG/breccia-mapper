# Admin Usage

You will need to log in with an administrator account to perform these actions.

:::{important}
Admin dashboard: this is the admin section of the site, accessed by clicking `Admin` on the navigation bar at the top.
:::

## Inviting Users

Please see [Configuration](2-configuration#inviting-users).

## Deleting Users

If you wish to permanently delete a user and their data:

1. Open the admin dashboard and click `Users`, in the `PEOPLE` section.
2. Locate and click the user you wish to delete.
3. Scroll to the bottom of the page and click `Delete`.

## Disable Login for a User

If you wish to disable login for a user but retain their data (relationships and personal details):

1. Open the admin dashboard and click `Users`, in the `PEOPLE` section.
2. Locate and click the user you wish to delete.
3. Under `Permissions`, disable `Active`.
4. Scroll to the bottom and click `Save`.

To allow the user to log in again, perform the same actions but enable the `Active` option.

## Promoting a User to Administrator

The user you wish to make an administrator must already exist. Then:

1. Open the admin dashboard and click `Users`, in the `PEOPLE` section.
2. Locate and click the user you wish to delete.
3. Under `Permissions`, enable `Staff status` and `Superuser status`.
4. Scroll to the bottom and click `Save`.

## Edit an Activity

1. Open the admin dashboard and click `Activities`, in the `ACTIVITIES` section.
2. Locate and click the activity you wish to update.
3. Update the fields appropriately.
4. Finally click `Save`.

## View a Map of People and Organisations

To view an interactive map showing people and organisations that have recorded their locations, click `Map` in the banner at the top of the screen. You can toggle the visibility of people and organisations with the buttons at the top of the page.

Nodes for people on the map have the same colour as the buttons at the top of the page. Nodes can be clicked the name of the person or organisation they represent, and this can be clicked to view their profile.

:::{note}
This page is only available to administrators.
:::

## View a Graph of the Network

The network mapper provides an interface to view the network as a graph. To access it, click `Network` in the banner at the top of the screen. This graph can be customised with various filters as shown on the page. Setting the date will show the state of the network as it was on the given date. People and organisations can be anonymised, organisations can be hidden, and the graph can be downloaded as an image. These options are all available as buttons on the page.

The graph can also be manipulated with the mouse.

:::{note}
This page is only available to administrators.
:::

## Export Data

All data relating to the network can be exported as CSV files. To do this, click `Export` in the banner at the top of the screen, then click `Export` next to the data you wish to export. This can then be manipulated as a spreadsheet or with a tool like R to perform more complex data analysis than is available natively in the network mapper.

:::{note}
This page is only available to administrators.
:::
