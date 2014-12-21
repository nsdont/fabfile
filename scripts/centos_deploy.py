import os.path as op

from fabric.api import run, prompt, put, sudo, cd, puts
from getpass import getpass


BASE_DIR = op.dirname(__file__)


def test():
    redis_file = op.join(BASE_DIR, 'deploy_soft/redis-2.8.17.tar.gz')
    put(redis_file, '/tmp/redis.tar.gz')


def ssh_setup():
    user = prompt("Please input new user:")

    run('useradd {}'.format(user))

    sudo('mkdir -p ~/.ssh', user=user)
    ssh_pubfile = prompt('Please input ssh pub key(default: ~/.ssh/abstack/'
                         'id_rsa.pub):')
    ssh_pubfile = ssh_pubfile if ssh_pubfile else '~/.ssh/abstack/id_rsa.pub'
    home = '/home/{}'.format(user)
    remote_pubfile = '{}/.ssh/authorized_keys'.format(home)
    put(ssh_pubfile, remote_pubfile)

    run('chmod -R 700 {}/.ssh'.format(home))
    run('chown -R {0}:{0} {1}/.ssh'.format(user, home))

    sudo('ssh-keygen', user=user)


def install():
    enable_develop_repo()
    install_base()
    install_python()
    install_redis()
    install_nginx()
    install_nodejs()


def enable_develop_repo():
    run('rpm -ivh ftp://ftp.pbone.net/mirror/download.fedora.redhat.com/pub/'
        'fedora/epel/6/i386/epel-release-6-8.noarch.rpm')
    run('rpm -Uvh http://rpms.famillecollet.com/enterprise/remi-release-6.rpm')


def install_redis():
    version = '2.8.17'
    puts('Install Redis {}'.format(version))
    with cd('/tmp'):
        file_path = op.join(BASE_DIR,
                            'deploy_soft/redis-{}.tar.gz'.format(version))
        put(file_path, '/tmp/redis-{}.tar.gz'.format(version))
        run('tar xz -f redis-{}.tar.gz'.format(version))
        with cd('redis-{}'.format(version)):
            run('make')
            run('make test')
            run('make install')


def install_nginx():
    puts('Install Nginx')
    run("echo '[nginx]' > /etc/yum.repos.d/nginx.repo")
    run("echo 'name=nginx repo' >> /etc/yum.repos.d/nginx.repo")
    run("echo 'baseurl=http://nginx.org/packages/centos/$releasever/"
        "$basearch/' >> /etc/yum.repos.d/nginx.repo")
    run("echo 'gpgcheck=0' >> /etc/yum.repos.d/nginx.repo")
    run("echo 'enabled=1' >> /etc/yum.repos.d/nginx.repo")

    run('yum -y install nginx')


def install_python():
    install_python2()
    install_python3()
    install_pip()
    install_virtualenv()


def install_base():
    puts('Install base software..')
    run('yum -y --enablerepo=remi groupinstall "Development tools"')
    run('yum -y --enablerepo=remi install zlib-devel bzip2-devel openssl-devel'
        ' ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel '
        'db4-devel libpc ap-devel xz-devel git libxslt-devel '
        'libjpeg-turbo-devel openjpeg-devel turbojpeg-devel')


def install_python2():
    version = '2.7.6'
    puts('Install Python {}'.format(version))
    with cd('/tmp'):
        file_path = op.join(BASE_DIR,
                            'deploy_soft/Python-{}.tar.xz'.format(version))
        put(file_path, '/tmp/Python-{}.tar.xz'.format(version))
        run('tar xf Python-{}.tar.xz'.format(version))
        with cd('Python-{}'.format(version)):
            run('./configure --prefix=/usr/local --enable-unicode=ucs4 --enab'
                'le-shared LDFLAGS="-Wl,-rpath /usr/local/lib"')
            run('make && make altinstall')


def install_python3():
    version = '3.3.5'
    puts('Install Python {}'.format(version))
    with cd('/tmp'):
        file_path = op.join(BASE_DIR,
                            'deploy_soft/Python-{}.tar.xz'.format(version))
        put(file_path, '/tmp/Python-{}.tar.xz'.format(version))
        run('tar xf Python-{}.tar.xz'.format(version))
        with cd('Python-{}'.format(version)):
            run('./configure --prefix=/usr/local --enable-shared LDFLAGS="-Wl'
                ',-rpath /usr/local/lib"')
            run('make && make altinstall')


def install_pip():
    puts('Install pip')
    with cd('/tmp'):
        run('wget https://bootstrap.pypa.io/get-pip.py')

        puts('Install pip2.7')
        run('python2.7 get-pip.py')

        puts('Install pip3.3')
        run('python3.3 get-pip.py')

        run('mkdir -p ~/.pip')
        run("echo '[global]' > ~/.pip/pip.conf")
        run("echo 'index-url = http://pypi.v2ex.com/simple/' >>"
            " ~/.pip/pip.conf")


def install_virtualenv():
    puts('Install virtualenv')
    run('pip2.7 install virtualenv')


def install_mysql():
    puts('Install MySQL')
    run('yum -y --enablerepo=remi install mysql mysql-server mysql-devel')
    run('service mysqld start')
    mysql_password = ''
    while not mysql_password:
        mysql_password = getpass('Please input mysql password')
    run("/usr/bin/mysqladmin -u root password '{}'".format(mysql_password))
    sql = ("GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '{}' "
           "WITH GRANT OPTION; FLUSH PRIVILEGES;").format(mysql_password)
    shell = 'mysql -u{user} -p{password} -e "{sql}"'
    shell.format(user='root', password=mysql_password, sql=sql)
    run(shell)


def install_postgresql():
    puts('Install postgresql')
    run('yum -y localinstall http://yum.postgresql.org/9.3/redhat/rhel-6-x86'
        '_64/pgdg-centos93-9.3-1.noarch.rpm')

    run('yum -y install postgresql93-server postgresql93-devel')
    run('service postgresql-9.3 initdb')
    run('chkconfig postgresql-9.3 on')
    run('service postgresql-9.3 start')


def install_nodejs():
    version = '0.10.33'
    puts('Install NodeJS {}'.format(version))
    with cd('/tmp'):
        file_path = op.join(BASE_DIR,
                            'deploy_soft/node-v{}.tar.gz'.format(version))
        put(file_path, '/tmp/node-v{}.tar.gz'.format(version))
        run('tar xz -f node-v{}.tar.gz'.format(version))
        with cd('node-v{}'.format(version)):
            run('make')
            run('make install')
        run('npm install -g bower')


def deploy():
    run('mkdir -p ~/.pip')
    run("echo '[global]' > ~/.pip/pip.conf")
    run("echo 'index-url = http://pypi.v2ex.com/simple/' >>"
        " ~/.pip/pip.conf")
    run('pip install supervisor')
