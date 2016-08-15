#!/bin/python
import os
import paramiko
import botocore
import boto3
import sys
from multiprocessing.dummy import Pool as ThreadPool

# grab params
conf = {
    'sftp_user': str(sys.argv[1]),
    'sftp_pass': str(sys.argv[2]),
    'sftp_host': str(sys.argv[3]),
    's3_bucket': str(sys.argv[4]),
    's3_path': str(sys.argv[5]),
    'concurrency': str(sys.argv[6])
}

# Set s3 boto3 objects
s3 = boto3.client('s3')
s3res = boto3.resource('s3')

# check to ensure the tmp directory is there
tmpdir = '/tmp/pulled/'
try:
    os.stat(tmpdir)
except:
    os.mkdir(tmpdir)


# Log Function diff
def log(text):
    print(str(text))


# Function to check if file is already backed up
# Saves several seconds per file
def backup_exists(ftpfile):
    exists = 'False'

    try:
        s3res.Object(conf['s3_bucket'], conf['s3_path'] + ftpfile).load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            exists = 'False'
        else:
            exists = 'False'
            raise
    else:
        exists = 'True'
    return exists


# Main handler.  Not expecting args.
def handler(event, context):

    # Start sftp connection
    log("Start SFTP Connection to " + conf['sftp_host'] + " ...")
    try:
        transport = paramiko.Transport((conf['sftp_host'], 22))
        transport.connect(username=conf['sftp_user'], password=conf['sftp_pass'])
    except Exception as e:
        log('Error connecting to SFTP endpoint')
        log(e)
    with paramiko.SFTPClient.from_transport(transport) as sftp:
        # paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)
        log('Building list of files and dirs...')
        files1 = []
        dirs = []
        for i in sftp.listdir():
            lstatout = str(sftp.lstat(i)).split()[0]
            if 'd' not in lstatout:
                files1.append(str(i))
            if 'd' in lstatout:
                dirs.append(str(i))
        for d in dirs:
            sublist = []
            sublist = sftp.listdir('./' + d)
        for f in sublist:
            files1.append(d + '/' + f)
            sublist = None
        log(files1)
        sftp.close()

    def check_and_backup(f):
        try:
            with paramiko.SFTPClient.from_transport(transport) as sftp:
                log("Found: " + f)
                if backup_exists(f) == 'False':
                    log('Backing up... ' + f)
                    sftp.get(f, tmpdir + f)
                    log('Uploading to S3')
                    s3res.meta.client.upload_file(tmpdir + f, conf['s3_bucket'], conf['s3_path'] + f)
                    os.remove(tmpdir + f)
                    log('Done with ' + f)
                sftp.close()
        except paramiko.SSHException:
            log("Hit a rate limit connecting to SFTP: " + str(f))
            pass
        except Exception as e:
            log('Trying to backup ' + f + ' found this error: ' + str(e))
            sftp.close()
            pass
    # sftp.close()


    # Step through files
    try:
        pool = ThreadPool(concurrency)
        pool.map(check_and_backup, files1)
        pool.close()
        pool.join()
    except Exception as e:
        log('Through error while starting the threads...  Error was: ' + e)
    sftp.close()

handler(1, 2)

