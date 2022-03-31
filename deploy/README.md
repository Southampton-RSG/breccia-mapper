# BRECcIA Mapper Deployment

BRECcIA Mapper is intended to be deployed using Ansible and Docker.
It has been tested on RHEL7 and RHEL8, though with minor modification to the Ansible playbook it is expected to deploy correctly on other Linux variants (e.g. Ubuntu).

## Development Deployment

Prerequisites:

- [Vagrant](https://www.vagrantup.com/)
- [Ansible](https://www.ansible.com/)

Using Vagrant, we can create a virtual machine and deploy BRECcIA Mapper using the same provisioning scripts as a production deployment.
To deploy a local development version of BRECcIA Mapper inside a virtual machine, use:

```
vagrant up
```

Once this virtual machine has been created, to redeploy use:

```
vagrant provision
```

And to stop the virtual machine use:

```
vagrant halt
```

For further commands see the [Vagrant documentation](https://www.vagrantup.com/docs/cli).

## Production Deployment

Prerequisites:

- [Ansible](https://www.ansible.com/)

To perform a production deployment of BRECcIA Mapper:

1. Copy the `inventory.example.yml` to `inventory.yml`
2. Edit this file:
  - Use your server's hostname instead of `example.com`
  - Disable debugging
  - Replace the secret key with some text known only to you
3. Run the Ansible playbook with this inventory file using:

```
ansible-playbook playbook.yml -i inventory.yml -K -k -u <SSH username>
```

This will ask for your SSH and sudo passwords for the server, before deploying.
To redeploy updates, the same command can be run again - it's safe to redeploy on top of an existing deployment.
