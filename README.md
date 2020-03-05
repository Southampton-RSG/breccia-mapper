# BRECcIA-Mapper (provisional name)

The canonical source for this project is hosted on [GitHub](https://github.com/Southampton-RSG/breccia-mapper),
please log any issues there.

BRECcIA-Mapper is a web app to collect and explore data about the relationships between researchers and their stakeholders on large-scale, multi-site research projects.

TODO motivations, usage, license

## Technology

This project is written in Python using the popular [Django](https://www.djangoproject.com/) framework.

An [Ansible](https://www.ansible.com/) playbook is provided which is designed for deployment on RHEL7 or CentOS7 Linux systems.  This installs and configures:
- MySQL
- Nginx
- Django + BRECcIA-Mapper

TODO deployment instructions