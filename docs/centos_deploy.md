# CentOS 6.5 部署

> 本教程使用的fabfile是scripts/centos_deploy.py

##### 目录:
一. 配置ssh
二. 分区
三. 安装基础依赖库, 配置软件源(python, nginx, redis, 数据库)
四. 数据库配置

##### 一. 配置ssh
1. 执行`fab -H root@servername ssh_setup`
2. 配置sshd文件
```
    vim /etc/ssh/sshd_config
    > Port 60237
    > PasswordAuthentication no
    > PermitRootLogin no
    service sshd restart
```
3. 配置本地ssh/config文件
```
Host server_name
    user username
    HostName ip
    Port port
    IdentityFile  ~/.ssh/abstack/id_rsa
```

##### 二. 分区

1.查看数据盘
```
在没有分区和格式化数据盘之前，使用 "df -h"命令，是无法看到数据盘的，可以使用"fdisk -l"命令查看。
```
2.对数据盘进行分区
```
执行"fdisk -S 56 /dev/xvdb"命令，对数据盘进行分区;
根据提示，依次输入"n"，"p, "1"，两次回车，"wq"，分区就开始了，很快就会完成。
```
3.查看新的分区
```
使用"fdisk -l"命令可以看到，新的分区xvdb1已经建立完成了。
```
4.格式化新分区
```
使用"mkfs.ext4 /dev/xvdb1"命令对新分区进行格式化，格式化的时间根据硬盘大小有所不同。(也可自主决定选用 ext4 格式) 
```
5.添加分区信息
```
使用"echo '/dev/xvdb1  /data ext4    defaults    0  0' >> /etc/fstab"（不含引号）命令写入新分区信息。然后使用"cat /etc/fstab"命令查看，出现以下信息就表示写入成功。
```
6.挂载新分区
```
使用"mount -a"命令挂载新分区，然后用"df -h"命令查看，出现以下信息就说明挂载成功，可以开始使用新的分区了。
```

##### 三. 安装基础依赖库, 配置软件源(python, nginx, redis, 数据库)
1. fab -H root@servername install

##### 四. 数据库配置
###### mysql
```
fab -H root@servername install_mysql
```

###### postgresql
```
fab -H root@servername install_postgresql
```
安装之后, 先设置密码
```
> psql -U postgres template1
template1=# alter user postgres password 'YourNewPassword';
```
在设置pg_hda.conf
```
# "local" is for Unix domain socket connections only
local   all     all             md5
# IPv4 local connections:
host    all     all     all     md5
```
如果想要开启外网访问就需要修改postgresql.conf
```
listen_addresses = '*'
```
