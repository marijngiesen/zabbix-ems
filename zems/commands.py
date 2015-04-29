try:
    from commandr import command
except ImportError:
    command = None
    import sys
    print "Error: Commandr module cannot be loaded, please install using 'pip install commandr'"
    sys.exit(1)

@command("apache")
def apache(metric=None):
    from zems.apache import Apache

    run_test(Apache(), metric)


@command("dhcpd")
def haproxy(metric=None, firstip=None):
    from zems.dhcpd import Dhcpd

    run_test(Dhcpd(), metric, firstip=firstip)


@command("haproxy")
def haproxy(metric=None, pxname=None, svname=None):
    from zems.haproxy import HAProxy

    run_test(HAProxy(), metric, need_root=True, pxname=pxname, svname=svname)


@command("mysql")
def sphinx(metric=None):
    from zems.mysql import MySQL

    run_test(MySQL(), metric)

@command("nginx")
def nginx(metric=None):
    from zems.nginx import Nginx

    run_test(Nginx(), metric)


@command("php-fpm")
def phpfpm(metric=None, pool=None):
    from zems.phpfpm import PhpFpm

    run_test(PhpFpm(), metric, pool=pool)


@command("radiator")
def phpfpm(metric=None):
    from zems.radiator import Radiator

    run_test(Radiator(), metric)


@command("rdiff-backup")
def rdiffbackup(metric=None):
    from zems.rdiffbackup import RdiffBackup

    run_test(RdiffBackup(), metric, need_root=True)


@command("redis")
def redis(metric=None, db=None):
    from zems.redis import Redis

    run_test(Redis(), metric, db=db)


@command("sphinx")
def sphinx(metric=None):
    from zems.sphinx import Sphinx

    run_test(Sphinx(), metric)


def run_test(test, metric, need_root=False, **kwargs):
    if metric is not None:
        if need_root:
            test.need_root()
        test.get(metric, **kwargs)
    else:
        test.print_metrics()
