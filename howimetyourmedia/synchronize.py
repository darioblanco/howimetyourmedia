# -*- coding: UTF-8 -*-

import os
from datetime import datetime
from stat import S_ISDIR

import paramiko

from howimetyourmedia.secret import HOST, USER, PASSWORD

LOCAL_PATH = '/home/media'
REMOTE_PATH = '/home/deluge/Downloads'


def sync_movies(sftp, last_timestamp):
    """Connects to the remote movies folder, and downloads everything that is
    new in the first path level
    """
    local_movies_path = os.path.join(LOCAL_PATH, 'Movies')
    remote_movies_path = os.path.join(REMOTE_PATH, 'Movies')

    # Retrieve the list of file/directories in Movies
    file_list = sftp.listdir_attr(path=remote_movies_path)
    for f in file_list:
        if f.st_mtime > last_timestamp:
            # The file is new and must be downloaded
            # TODO: what if it is a directory???
            print "Downloading file {0}".format(f.filename)
            sftp.get(os.path.join(remote_movies_path, f.filename),
                     os.path.join(local_movies_path, f.filename))


def sync_series(sftp):
    """Connects to the remove series folder, loops through every folder in
    the first path level, and downloads new files from each folder
    """
    local_series_path = os.path.join(LOCAL_PATH, 'Series')
    remote_series_path = os.path.join(REMOTE_PATH, 'Series')

    # Retrieve the list of file/directories in Series
    dir_list = sftp.listdir_attr(path=remote_series_path)
    for d in dir_list:
        # Ignore files, only check directories (proper TV shows)
        if S_ISDIR(d.st_mode):
            tvshow_path = os.path.join(remote_series_path, d.filename)
            # Retrieve the list of file/directories in this TV Show
            file_list = sftp.listdir_attr(path=tvshow_path)
            for f in file_list:
                if f.st_mtime > last_timestamp:
                    # The file is new and must be downloaded
                    # TODO: what if it is a directory???
                    print "Downloading file {0}".format(f.filename)
                    sftp.get(os.path.join(tvshow_path, f.filename),
                             os.path.join(local_series_path, d.filename,
                                          f.filename))


if __name__ == '__main__':
    # Save current time as a timestamp for storing it after the script success
    now = datetime.now().strftime('%s')

    # Retrieve a previous timestamp for performing an incremental download
    if os.path.isfile('lastchecked'):
        # We ran the script before. download only new items
        with open('lastchecked', 'rb') as check_file:
            last_timestamp = int(check_file.read())
    else:
        # First time we run the script, we will download everything
        last_timestamp = 0

    # Connect to the desired host through SFTP
    transport = paramiko.Transport((HOST, 22))
    transport.connect(username=USER, password=PASSWORD)
    sftp = paramiko.SFTPClient.from_transport(transport)

    # Perform the synchronization
    sync_movies(sftp, last_timestamp)
    sync_series(sftp, last_timestamp)

    # Close the SFTP connection
    sftp.close()
    transport.close()

    # If everything is fine, we store the date for future incremental runs
    with open('lastchecked', 'wb') as check_file:
        check_file.write(now.strftime('%s'))
