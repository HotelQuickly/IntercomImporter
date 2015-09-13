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

Intercom API Id, Intercom API Key for accessing your Intercom account and the user url (default url is provided inside script) are needed in config to add/update users to Intercom
The timeout for Intercom request is the time gap between Intercom requests in the event of error, upto 50 retries will be done. The program will iterate through the CSV file and add/update users to Intercom one by one.

Allowed parameters for user in Intercom - any other will be discarded, please specify data type for custom attributes correctly in config, wrong data types prevent data being saved for users:

user_id	- if no email	a unique string identifier for the user. It is required on creation if an email is not supplied.

email - if no user_id	the user’s email address. It is required on creation if a user_id is not supplied.

id - The id may be used for user updates.

signed_up_at - The time the user signed up

name - The user’s full name

last_seen_ip - An ip address (e.g. “1.2.3.4”) representing the last ip address the user visited your application from. (Used for updating location_data)

custom_attributes - A hash of key/value pairs containing any other data about the user you want Intercom to store.*

last_seen_user_agent - The user agent the user last visited your application with. eg. "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9"

last_request_at - A UNIX timestamp (in seconds) representing the date the user last visited your application.

unsubscribed_from_emails - A boolean value representing the users unsubscribed status. default value if not sent is false.

update_last_request_at - A boolean value, which if true, instructs Intercom to update the users’ last_request_at value to the current API service time in UTC. default value if not sent is false.

new_session - A boolean value, which if true, instructs Intercom to register the request as a session.



Hipchat settings require the API key, room id where the notification is to be sent and a from name (hipchat allows names of 1 to 15 characters in length).
Hipchat maybe enabled or disabled, the root API URL is specified already.

Slack settings require the incoming webhook url. Slack Channel can be specified, default webhook channel will be used otherwise. A user can be used instead of a channel by prepending the username with "@". Username and icon url , emoji are optional, default ones for the channel will be used otherwise.
Slack maybe enabled or disabled.


CSV settings are used to find delimiter of CSV file(default is comma) and Intercom parameter mapping.

Run python export_csv.py to run the program.

If you have specified to use specific file names, you can use python export_csv.py filename to choose the file.

If you have not mentioned the local folder, current folder is taken as the local folder, you may use relative paths for files in current directory/sub directories then or absolute paths for choosing files from other directories/disks.


Start and end notifications are sent to hipchat. Start notification will be yellow. End notification will be green for success and red for error. End notification on success will contain number of users added.

Notifications for start, end and error in execution will be sent to Slack if Slack is used.

Log files will be stored in the mentioned log folder if logging is enabled, if no folder is mentioned, a log folder will be created in the current directory with two files on each run. One debug log and one error log per run.