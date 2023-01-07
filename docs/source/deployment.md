# Deployment

The BRECcIA Relationship Mapper can be deployed in a variety of ways, most of which utilise Docker.
Ansible deployment has been tested on RHEL7 and RHEL8.

, and Ubuntu 22.04 LTS.

## Development Deployment

Prerequisites:

- [Vagrant](https://www.vagrantup.com/)
- [Ansible](https://www.ansible.com/)

Using Vagrant, we can create a virtual machine and deploy BRECcIA Mapper using the same provisioning scripts as a production deployment.
To deploy a local development version of BRECcIA Mapper inside a virtual machine, first navigate to the `deploy` folder:

```bash
cd deploy
```

And then start the virtual machine using:

```bash
vagrant up
```

Once this virtual machine has been created, provision the virtual machine (deploying the relationship mapper) using:

```bash
vagrant provision
```

This installs the relationship mapper and makes it available on the local machine at `http://localhost:8080`.
If you wish to make this accessible from other devices on your local network, replace the following line in `deploy/Vagrantfile`:

```ruby
config.vm.network "forwarded_port", guest: 80, host: 8080, host_ip: "127.0.0.1"
```

with:

```ruby
config.vm.network "forwarded_port", guest: 80, host: 8080
```

To stop the virtual machine run the following, in the `deploy` directory:

```
vagrant halt
```

For further commands see the [Vagrant documentation](https://www.vagrantup.com/docs/cli).

## Production Deployment

### Ansible (Recommended)

Prerequisites:

- [Ansible](https://www.ansible.com/)

:::{note}
Deployment with Ansible has been tested on RHEL7 and RHEL8, but is compatible with other Linux distributions with minor changes to the playbook (`deploy/playbook.yml`)
:::

To deploy the BRECcIA Relationship Mapper with Ansible:

1. Copy `settings.example.ini` to `settings.ini`
2. Edit this file as desired. Note there is no requirement to change any of these variables, but it is recommended.
3. Copy `inventory.example.yml` to `inventory.yml`
4. Edit this file to reflect your Ansible setup:
  - Use your server's hostname instead of `example.com`
  - Replace the secret key with some text known only to you
5. Run the Ansible playbook `deploy/playbook.yml` with this inventory file using:

```
ansible-playbook playbook.yml -i inventory.yml -K -k -u <SSH username>
```

This will ask for your SSH and sudo passwords for the server before deploying.
To redeploy updates, the same command can be run again - it's safe to redeploy on top of an existing deployment.

### Docker Compose

Prerequisites:

- [Docker Compose](https://docs.docker.com/compose) (installed by default with most [Docker](https://docker.com/) installs)

:::{note}
Deployment with Docker has been tested on RHEL7, RHEL8, and Ubuntu 22.04 LTS
:::

To deploy the BRECcIA Relationship Mapper with Docker:

1. Copy `deploy/settings.example.ini` to `breccia_mapper/settings.ini`
2. Edit this file as desired. Note there is no requirement to change any of these variables, but it is recommended.
3. Create the database using:

```bash
touch db.sqlite3
```

4. Set the `DEBUG` and `SECRET_KEY` values in `docker-compose.yml`.
  - The secret key should be a long, random string that only you know. Replace `${DJANGO_SECRET_KEY}` with this key.
  - Debug can be `True` or `False`. Replace `${DJANGO_DEBUG}` with this value.
  - You can also set these via environment variables on the host machine. The appropriate environment variables are `DJANGO_SECRET_KEY` and `DJANGO_DEBUG`.
5. Start the containers with the following command (you may need to use `sudo`):

```bash
docker compose up -d
```

6. Create a superuser by running the following, and enter their details when prompted:

```bash
docker compose exec -it server /bin/bash -c "/app/manage.py createsuperuser"
```

