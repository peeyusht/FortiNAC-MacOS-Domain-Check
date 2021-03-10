#!/usr/bin/python3


###########################################################
"""
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



"""
Please populate the values in first 5 parameters in function main
"""




import sys
import paramiko
import requests
import json


# Main function
def main():
    #FortiNAC server IP Address and API Token
    serverIPAddress = "<FortiNAC Eth0 IP Address"
    apiToken = "<FortiNAC API token"

    #Username and Password to login to client/host (String Type)
    username = "<username>"
    password = "<password>"
    domainName = "<MS AD domain to verify>"

    message = "1. " + str(sys.argv)
    writeToFile( message )

    # Arguments received
    #arguments = str(sys.argv)
    hostIPStr = str(sys.argv[1])
    print("HostIP: ", hostIPStr)

    # Store Host IP, Username, Password and AD Domain in variables
    hostIP = hostIPStr

    message = "2. HostIP: " + hostIP
    writeToFile( message )

    # fetch hostID using IP address of host
    hostDetails = getHostIDUsingIP(serverIPAddress, hostIP, apiToken)

    # extract HostID and Operating System of endpoint
    hostID = str(hostDetails['results'][0]['id'])
    operatingSystem = str(hostDetails['results'][0]['operatingSystem'])

    message = "7. HostID: " + hostID
    writeToFile( message )

    if checkADDomain(hostIP, operatingSystem, username, password, domainName):
        message = "4. Domain Joined Host"
        writeToFile( message )
        domainJoinedHost = 0
        role = "Domain-Joined"
    else:
        message = "4. Domain Not Joined Host"
        writeToFile( message )
        domainJoinedHost = 1
        role = "Non-Domain-Joined"

    message = "5. DomainJoined Host: " + str(domainJoinedHost) + "Role: " + role
    writeToFile( message )

    # Change AtRisk and Role of Host
    response = changeHostRole( hostID, operatingSystem, role, serverIPAddress, apiToken )
    message = "8.9 Test"
    writeToFile( message )

    message = "9. Arguments: " + str(sys.argv) + " HostID: " + str(hostID) + " HostIP: " + hostIP + " Response: " + str(response)
#    message = "9. Arguments: " + str(sys.argv)
    writeToFile( message )

    sys.exit(domainJoinedHost)
#################################################################


# Function to match domain of computer using SSH
def checkADDomain(hostIP, operatingSystem, username, password, domainToMatch):
    # Initialize the SSH client
    host = paramiko.SSHClient()

    writeToFile ("2.5 HostIP: " + hostIP)

    # Add to known hosts
    host.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        host.connect(hostname=hostIP, username=username, password=password)
    except:
        writeToFile ("2.5  Cannot connect to the SSH server")
        print("[!] Cannot connect to the SSH Server")
        exit()

    writeToFile ("2.6. Before If: OS Name..."+ operatingSystem[:3] + "....")
    # Create a command to execute
    if (operatingSystem[:3] == "Mac"):
        command = "dsconfigad -show | awk '/Active Directory Domain/{print $NF}'"
        writeToFile ("2.6. Inside Mac OS check If")
    if (operatingSystem[:3] == "Ubu"):
        command = "realm list | grep domain-name"
        writeToFile ("2.6. Inside Linux OS check If")
    #Execute command check if machine is joined to Freecharge domain or not
    stdin, stdout, stderr = host.exec_command(command)
    outputToMatch = str(stdout.read().decode())

    writeToFile ("2.7. After if to check Operating system")

    host.close()

    err = stderr.read().decode()
    if err:
        print(err)

    if domainToMatch == outputToMatch[:-1]:
        writeToFile ("3. Domain Matched " + domainToMatch + " " + outputToMatch)
        return True
    else:
        writeToFile ("3. Domain Not Matched " + domainToMatch + " " + outputToMatch)
        return False
###########################################################################


# Function to fetch ID of host from FortiNAC server
def getHostIDUsingIP(serverIPAddress, hostIPAddress, apiToken):
    # API to get host ID by IP
    # https://<serverIPAddress>:8443/api/v2/host/by-ip/<hostIPAddress>

    ###FortiNAC API variables######
    fortiNACAPIToken = apiToken
    fortiNACAPIURLBase = "https://" + serverIPAddress + \
        ":8443/api/v2/host/by-ip/" + hostIPAddress
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer {0}'.format(fortiNACAPIToken)}

    # Fetch data using API
    response = requests.get(fortiNACAPIURLBase, headers=headers, verify=False)

    # Convert text to JSON format
    hostDetails = json.loads(response.text)

    # extract HostID and Operating System of endpoint
    hostID = str(hostDetails['results'][0]['id'])
    operatingSystem = str(hostDetails['results'][0]['operatingSystem'])

    message = "6. HostID: " + hostID + " Operating System: " + operatingSystem[:3]
    writeToFile (message)
    return hostDetails
###########################################################################


# Change Host Risk status (atRisk) and role
def changeHostRole(hostID,atRisk, role, serverIPAddress, apiToken):
    # API to get host ID by IP
    # https://<serverIPAddress>:8443/api/v2/host/by-ip/<hostIPAddress>

    arrayHostID = [hostID]

    ###FortiNAC API variables######
    fortiNACAPIToken = apiToken
#    fortiNACAPIURLBase = "https://" + serverIPAddress + \
#        ":8443/api/v2/host/" + str(hostID)
    fortiNACAPIURLBase = "https://" + serverIPAddress + \
        ":8443/api/v2/host/set-role"

    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Authorization': 'Bearer {0}'.format(fortiNACAPIToken)}
    files = []
#    payload = {'atRisk': atRisk, 'role': role}
    payload = {'id':arrayHostID, 'role': role}

    message = "8. " + str(payload) + " URL: " + fortiNACAPIURLBase
    writeToFile (message)

    # Post risk and role data to host using API
    response = requests.post( fortiNACAPIURLBase, headers=headers, data=payload, files=files, verify=False)

    message = "8.1. Payload" + str(payload) + " " + "Response: " + str(response.text.encode('utf8'))
    writeToFile (message)

    return response
    # print(response.text.encode('utf8'))


#############################################################################


## Write to test message to File
def writeToFile(text):
    file = open("/home/cm/scripts/MacDomainCheck", "a")
    file.write(text)
    file.write("\n")
    file.close()
##############################################################

# Calling Main function
if __name__ == "__main__":
    main()
