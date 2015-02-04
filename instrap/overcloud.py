from __future__ import print_function

from fabric.api import task

from instrap import tmux, undercloud


def _setup(session_name='overcloud'):
    undercloud_ip = undercloud.ip()

    if not undercloud_ip:
        return

    tmux.create_session(session_name)
    tmux.run(session_name, "ssh stack@{}".format(undercloud_ip))
    tmux.run(session_name, "stack")

    tmux.run(session_name, 'sudo cp /root/tripleo-undercloud-passwords ~/')
    tmux.run(session_name, 'sudo cp /root/stackrc ~/')

    tmux.run(session_name, 'source ~/deploy-overcloudrc')
    tmux.run(session_name, 'source ~/tripleo-undercloud-passwords')
    tmux.run(session_name, 'source ~/stackrc')
    tmux.run(session_name, 'source /usr/share/instack-undercloud/deploy-virt-overcloudrc')  # NOQA


def _create_update(update, control, compute, blockstorage, swiftstorage):

    if not update:
        _setup()

    tmux.run('overcloud', 'export CONTROLSCALE={}'.format(control))
    tmux.run('overcloud', 'export COMPUTESCALE={}'.format(compute))
    tmux.run('overcloud', 'export BLOCKSTORAGESCALE={}'.format(blockstorage))
    tmux.run('overcloud', 'export SWIFTSTORAGESCALE={}'.format(swiftstorage))

    if not update:
        tmux.run('overcloud', 'time instack-deploy-overcloud --tuskar')
    else:
        tmux.run('overcloud', 'time instack-update-overcloud --tuskar')


@task
def deploy(control=1, compute=1, blockstorage=0, swiftstorage=0):
    _create_update(False, control, compute, blockstorage, swiftstorage)


@task
def update(control=1, compute=1, blockstorage=1, swiftstorage=1):
    _create_update(True, control, compute, blockstorage, swiftstorage)


@task
def delete():
    tmux.run('overcloud', 'time instack-delete-overcloud')


@task
def test():
    _setup('o-test')
    tmux.run('o-test', 'time instack-test-overcloud')


__all__ = ['deploy', 'update', 'delete', 'test']
