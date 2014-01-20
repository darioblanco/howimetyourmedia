howimetyourmedia
=================

Specific folder synchronization using `paramiko`.

Connects to your remote server through a SFTP account, and downloads only new content into your local folders.

It will download the new items into specific folders:
- "Movies" folder (contains all the movies in 1 folder)
- "Series" folders (contains a list of TV Shows, 1 folder per TV show)

Ideal when you have a seedbox and you want to update your NAS or local computer periodically, just create a cronjob that runs `synchronize.py` and done!
