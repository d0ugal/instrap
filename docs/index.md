# Instrap - Bootstrapping Instack.

Instrap is a set of utilities for automating otherwise manual
steps when working with an instack development environment.

This means we primarily help automate the instructions found here:

    https://repos.fedorapeople.org/repos/openstack-m/instack-undercloud/html/

## Setup

I'd recommend doing this within a virtualenv, but that is
optional. Without it you may need sudo for the pip install.

```bash
git clone git@github.com:d0ugal/instrap.git
cd instrap
pip install -r requirements.txt
```

Then to view the commands run fab -l from within the directory.
The commands are explained below in some detail in a suggested
install flow.


## Commands

Instrap is based on Fabric and thus all commands are currently
invoked with the `fab` command.

To see a list of commands use `fab -l` and then each of them
can be called like this: `fab $HOST $COMMAND`
