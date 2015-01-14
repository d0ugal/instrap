from __future__ import print_function

from fabric.api import task

from instrap import tmux, undercloud


def _create_update(update, control, compute, blockstorage, swiftstorage):

    if update:

        undercloud_ip = undercloud.ip()

        if not undercloud_ip:
            return

        tmux.create_session("overcloud")
        tmux.run('overcloud', "ssh stack@{}".format(undercloud_ip))
        tmux.run('overcloud', "stack")

        tmux.run('overcloud', 'sudo cp /root/tripleo-undercloud-passwords ~/')
        tmux.run('overcloud', 'sudo cp /root/stackrc ~/')

    tmux.run('overcloud', 'export CONTROLSCALE={}'.format(control))
    tmux.run('overcloud', 'export COMPUTESCALE={}'.format(compute))
    tmux.run('overcloud', 'export BLOCKSTORAGESCALE={}'.format(blockstorage))
    tmux.run('overcloud', 'export SWIFTSTORAGESCALE={}'.format(swiftstorage))

    tmux.run('overcloud', 'source ~/deploy-overcloudrc')
    tmux.run('overcloud', 'source ~/tripleo-undercloud-passwords')
    tmux.run('overcloud', 'source ~/stackrc')
    tmux.run('overcloud', 'source /usr/share/instack-undercloud/deploy-virt-overcloudrc')  # NOQA

    if not update:
        tmux.run('overcloud', 'instack-deploy-overcloud --tuskar')
    else:
        tmux.run('overcloud', 'instack-update-overcloud --tuskar')


@task
def deploy(control=1, compute=1, blockstorage=0, swiftstorage=0):
    _create_update(False, control, compute, blockstorage, swiftstorage)


@task
def update(control=1, compute=1, blockstorage=1, swiftstorage=1):
    _create_update(True, control, compute, blockstorage, swiftstorage)


__all__ = ['deploy', 'update']
