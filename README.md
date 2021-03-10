# MacOS-Domain-Check

FortiNAC till v8.8.5 cannot send SMS using https API
I tried to create a python script to send SMS once guest is registered


Below are the pre-requisites and steps need to be taken to install the script

Requires Python3
Requires Python3 modules paramiko and requests using pip3

Temporarily change yum repo, so that Python3 can be install along with Python2.7 (default with FortiNAC)
To install Python3, follow below steps on FortiNAc client
copy next 2 lines and past it on FortiNAC CLI


mv /etc/yum.repos.d yum.repos.d.orig
mkdir /etc/yum.repos.d


create a new file /etc/yum.repos.d/CentOS.repo and paste below content

*****Copy below content********

[base]
name=CentOS $releasever – Base
baseurl=http://mirror.centos.org/centos/7/os/$basearch/
gpgcheck=0
enabled=1
[updates]
name=CentOS $releasever – Updates
baseurl=http://mirror.centos.org/centos/7/updates/$basearch/
gpgcheck=0
enabled=1
[extras]
name=CentOS $releasever – Extras
baseurl=http://mirror.centos.org/centos/7/extras/$basearch/
gpgcheck=0
enabled=1


*******Copy till above line and past that to /etc/tum.repos.d/CentOS.repo*************

copy next 3 lines and past it on FortiNAC CLI

yum repolist all
yum update
yum install python3

********Done with pre-requisites****

Copy this script to /home/cm/scripts of FortiNAC and use below 3 commands to change ownership and permission

cd /home/cm/scripts
chmod 755 Mac-Domain-Check.py
chown nac:nac MacDomain-Check.py




"""
Please populate the values in first 5 parameters in function main in the script
"""
