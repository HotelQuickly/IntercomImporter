# IntercomImporter
This python program is used to fetch user data from a CSV file and import it to Intercom. Hipchat and/or Slack notifications for the program status maybe used.

The program must be setup using the following steps.

Installboto must be run the first time to set up boto in python. boto is needed to access AWS S3. Use batch file for windows and shell script for Linux.

Check config file to see if all settings are correct.

AWS S3 settings are needed to access S3 storage and get CSV file from there. A temporary location to download files maybe mentioned, if not, the system's default temp directory/folder will be used.

To use local storage, use_aws should be "false" in config file.

For local storage, specify a folder where the file is located.

CSV files maybe selected based on a time format top choose the latest file. The filename should be timestamped as per the time format used in the config file.
Specific filenames may also be used.

Intercom API Id, Intercom API Key for accessing your Intercom account and the bulk user url (default url is provided inside script) are needed in config to add/update users to Intercom
The batch size maybe varied to regulate the number of users updated at one time. Intercom supports a maximum of around 100 objects in one request. You may vary this as per your upload speed and Intercom limitations.
The timeout for Intercom request must be set as per the number of users in one batch and your upload speed. The program will iterate through the CSV file and add/update users to Intercom in batches.

Hipchat settings require the API key, room id where the notification is to be sent and a from name (hipchat allows names of 1 to 15 characters in length).
Hipchat maybe enabled or disabled, the root API URL is specified already.

Slack settings require the incoming webhook url. Username and icon url , emoji are optional, default ones for the channel will be used otherwise.
Slack maybe enabled or disabled.


CSV settings are used to find delimiter of CSV file(default is comma) and Intercom parameter mapping.

Run python export_csv.py to run the program.

If you have specified to use specific file names, you can use python export_csv.py filename to choose the file.

If you have not mentioned the local folder, current folder is taken as the local folder, you may use relative paths for files in current directory/sub directories then or absolute paths for choosing files from other directories/disks.


Start and end notifications are sent to hipchat. Start notification will be yellow. End notification will be green for success and red for error. End notification on success will contain number of users added.

Notifications for start, end and error in execution will be sent to Slack if Slack is used.

Log files will be stored in the mentioned log folder if logging is enabled, if no folder is mentioned, a log folder will be created in the current directory with two files on each run. One debug log and one error log per run.