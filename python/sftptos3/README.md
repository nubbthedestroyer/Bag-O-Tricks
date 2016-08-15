## SFTPTOS3.py

###### A script for backing up files in sftp location to s3 bucket

### Intro
> This script is designed to iterate over a directory in an SFTP location and backup each file to an s3 bucket

### Requirements
> * Requires:
>   * Python 3.4
>   * The packages in the requirements.txt file.

### Usage
> Called like this
```
python3 -u sftptos3.py ${sftp_user} ${sftp_pass} ${sftp_host} ${s3_bucket