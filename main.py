import requests
import smtplib
import os # to access env variables
import paramiko
import boto3
import time
import schedule

EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
server_ip = '18.216.19.153'
app_url = 'http://18.216.19.153:8080/'
ec2_instance_id = 'i-0f9f0da5ca09386d6'
image_id = '6c4d9c89fd07'


def restart_server_and_container():
    # reboot the server
    print("Rebooting the server...")
    client = boto3.client('ec2')
    client.reboot_instances(InstanceIds=[ec2_instance_id])
    while True:
        response = client.describe_instance_status(InstanceIds=['i-0f9f0da5ca09386d6'])
        instance_state = response['InstanceStatuses'][0]['InstanceState']['Name']
        print(f"Instant state: {instance_state}")
        if instance_state == 'running':
            time.sleep(40)
            # restart the application
            restart_container()
            break


def send_notification(email_msg):
    # which email provider i want to use and port
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()  # start secure connection - encrypt communication
        smtp.ehlo()  # identify python application with mail server
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        message = f"Subject: SITE DOWN\n{email_msg}"
        # send from my account to my account
        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, message)


def restart_container():
    print('Restarting the application...')
    ssh = paramiko.SSHClient()
    # automatic confirm to add the host key to the server to allow the connection
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=server_ip, username='ec2-user', key_filename='/home/hossam/.ssh/id_rsa')
    print("Connection established with server")
    stdin, stdout, stderr = ssh.exec_command(f"sudo service docker start && docker start {image_id}")
    print(stdout.readlines())
    ssh.close()
    print('Application restarted')


def monitor_application():
    try:
        response = requests.get(app_url)
        # print(response.text)
        # print(response.status_code)
        if response.status_code == 200:
            print('Application is running successfully')
        else:
            print('Application Down. Fix it!')
            # send email to fix the problem
            msg = f'Application returned {response.status_code}.'
            send_notification(msg)
            # restart the application
            restart_container()

    except Exception as ex:
        print(f"Connection error happened: {ex}")
        msg = "Application not accessible at all"
        send_notification(msg)
        restart_server_and_container()


monitor_application()
# schedule.every(5).seconds.do(monitor_application)
#
# while True:
#     schedule.run_pending()






