# Deployment

The BRECcIA Network Mapper can be deployed in a variety of ways, most of which utilise Docker.
Ansible deployment has been tested on RHEL7 and RHEL8.

## Choosing How to Deploy

If you are an organisation deploying the app on a server, [Ansible](#ansible) is recommended. If Ansible is not used with your server, [Docker Compose](#docker-compose) or [][Vagrant](#vagrant) are recommended.

If you are an individual deploying the app on your local machine, [Docker Desktop](#docker-desktop) is recommended. However, if you are planning on making the app accessible to other people (outside your computer), we advise deploying the app on a server.

## Ansible

Prerequisites:

- [Ansible](https://www.ansible.com/)

:::{note}
Deployment with Ansible has been tested on RHEL7 and RHEL8, but is compatible with other Linux distributions with minor changes to the playbook (`deploy/playbook.yml`)
:::

To deploy the BRECcIA Network Mapper with Ansible:

1. Download and extract the deployment files from [the latest release](https://github.com/Southampton-RSG/breccia-mapper/releases/latest):

    ```bash
    curl https://github.com/Southampton-RSG/breccia-mapper/releases/latest/download/deploy-ansible.tar | tar xzv && cd network-mapper
    ```

2. Copy your logo (192x192 pixels) to `icon-192x192.png` in this folder.

3. Copy `example.env` to `.env`:

    ```bash
    cp example.env .env
    ```

4. Edit this file as desired. Note that some variables are required.
5. Copy `inventory.example.yml` to `inventory.yml`:

    ```bash
    cp inventory.example.yml inventory.yml
    ```

6. Edit this file to reflect your Ansible setup:
    - Use your server's hostname instead of `example.com`
7. If you would like a new superuser to be provisioned (e.g. during initial install), edit the `provision_superuser` variable in `playbook.yml` to `true`.
    - Then change the `superuser_*` options below it as desired.
8. Run the Ansible playbook `playbook.yml` with this inventory file using:

    ```bash
    ansible-playbook playbook.yml -i inventory.yml -K -k -u <SSH username>
    ```

This will ask for your SSH and sudo passwords for the server before deploying.
To redeploy updates, the same command can be run again - it's safe to redeploy on top of an existing deployment.

:::{warning}
If you changed the `provision_superuser` variable in `playbook.yml` to `true`, remember to change it back to `false`.
:::


## Docker Compose

Prerequisites:

- [Docker Compose](https://docs.docker.com/compose) (installed by default with most [Docker](https://docker.com/) installs)

:::{note}
Deployment with Docker has been tested on RHEL7, RHEL8, and Ubuntu 22.04 LTS
:::

To deploy the BRECcIA Network Mapper with Docker:

1. Download and extract the deployment files from [the latest release](https://github.com/Southampton-RSG/breccia-mapper/releases/latest):

    ```bash
    curl https://github.com/Southampton-RSG/releases/latest/download/deploy-docker.tar | tar xzv && cd network-mapper
    ```

2. Copy your logo (192x192 pixels) to `icon-192x192.png` in this folder.
3. Copy `example.env` to `.env`:

    ```bash
    cp example.env .env
    ```

4. Edit this file as desired. Note that some variables are required.
3. Create the database using:

    ```bash
    touch db.sqlite3
    ```

5. Start the containers with the following command (you may need to use `sudo`):

    ```bash
    docker compose up -d
    ```

6. If desired (e.g. on initial deployment), create a superuser by running the following, and enter their details when prompted:

    ```bash
    docker compose exec -it server /bin/bash -c "/app/manage.py createsuperuser"
    ```

:::{important}
If you don't create a superuser when you first deploy the app, you will be unable to log in.
:::

## Vagrant

Prerequisites:

- [Vagrant](https://www.vagrantup.com/)
- [Ansible](https://www.ansible.com/)

To deploy the BRECcIA Network Mapper with Vagrant:

1. Download and extract the deployment files from [the latest release](https://github.com/Southampton-RSG/breccia-mapper/releases/latest):

    ```bash
    curl https://github.com/Southampton-RSG/releases/latest/download/deploy-vagrant.tar | tar xzv && cd network-mapper
    ```

2. Copy your logo (192x192 pixels) to `icon-192x192.png` in this folder.
3. Copy `example.env` to `.env`:

    ```bash
    cp example.env .env
    ```

4. Edit this file as desired. Note that some variables are required.
5. If you would like a new superuser to be provisioned (e.g. during initial install), edit the `provision_superuser` variable in `playbook.yml` to `true`.
    - Then change the `superuser_*` options below it as desired.
6. To change where the app is accessible from, edit the `config.vm.network` line in `Vagrantfile`.
    - By default, the app is accessible only from `http://localhost:8080`.
    - To make it available from any IP address, replace `host: 8080, host_ip: "127.0.0.1"` with `host: 8080`.
    - To change the port the app is available on, edit `host: 8080`.
    - More details are available in the [Vagrant docs](https://developer.hashicorp.com/vagrant/docs/networking).
6. Start the virtual machine:

    ```bash
    vagrant up
    ```

7. Deploy the Network Mapper on the virtual machine:

    ```bash
    vagrant provision
    ```


:::{note}
To stop the virtual machine, run `vagrant halt` in this directory. More commands are explained in the [Vagrant docs](https://developer.hashicorp.com/vagrant/docs/cli).
:::

## Docker Desktop

Coming soon.

