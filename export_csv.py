#Imports
import os
import sys
import json
import csv
import re
import time
import base64
#AWS python Interface
from boto.s3.connection import S3Connection
import boto.s3.connection
#Differentiating urllibs between python 2 and python 3
if sys.version_info[0]<3:    
    import urllib
    import urllib2
else:
    import urllib
    import urllib.request as urllib2
#Config Loader for loading config file data and validating it
import config_loader

#Use local storage for CSV file
def use_local(config):
    try:
        if config.config_data["select_file_on_latest_time"]: #time based selection
            if config_data["local_folder"]=="":
                folder="."
            else:
                folder=config.config_data["local_folder"]
            files = [ f for f in os.listdir(config_data["local_folder"]) if os.path.isfile(os.path.join(config_data["local_folder"],f)) ]
            latest=""
            latest_time=None
            for f in files:
                config.log("File "+f)
                if latest_time is None:
                    latest_time=time.strptime(str(f).split('.')[0].split('/')[-1], "%Y-%m-%dT%H:%M:%S")
                    latest=f
                elif latest_time<time.strptime(str(f).split('.')[0].split('/')[-1], "%Y-%m-%dT%H:%M:%S"):
                    latest_time=time.strptime(str(f).split('.')[0].split('/')[-1], "%Y-%m-%dT%H:%M:%S")
                    latest=f
            if latest=="":
                print "\nError: No file found\n"
                config.log("\nError: No file found\n")
                config.log_error("\nError: No file found\n")
            else:
                print "Newest File is "+str(f)
                config.log("Newest File is "+str(f))
                if os.path.isfile(config.config_data["local_folder"]+f):
                    print "CSV file "+str(f).split('/')[-1]+" found"
                    config.log("CSV file "+str(f).split('/')[-1]+" found")
                    config.log("Reading CSV file")
                    read_csv_file(config, config.config_data["local_folder"]+f, int(config.config_data["intercom_batch_size"]))
                else:
                    print "\nError CSV file missing "+str(f).split('/')[-1]+"\n"
                    config.log("\nError CSV file missing "+str(f).split('/')[-1]+"\n")
                    config.log_error("\nError CSV file missing "+str(f).split('/')[-1]+"\n")
                    notify_hipchat(config, "Import to Intercom failed, AWS S3 error", "red")
                    notify_slack(config, "Import to Intercom failed, AWS S3 error")
        else: #specific file selection
            if os.path.isfile(config.config_data["local_folder"]+config.config_data["file_name"]):
                print "CSV file "+str(config.config_data["file_name"]).split('/')[-1]+" found"
                config.log("CSV file "+str(config.config_data["file_name"]).split('/')[-1]+" found")
                config.log("Reading CSV file")
                read_csv_file(config, config.config_data["local_folder"]+config.config_data["file_name"], int(config.config_data["intercom_batch_size"]))
            else:
                print "\nError CSV file missing "+str(config.config_data["file_name"]).split('/')[-1]+"\n"
                config.log("\nError CSV file missing "+str(config.config_data["file_name"]).split('/')[-1]+"\n")
                config.log_error("\nError CSV file missing "+str(config.config_data["file_name"]).split('/')[-1]+"\n")
                notify_hipchat(config, "Import to Intercom failed, AWS S3 error", "red")
                notify_slack(config, "Import to Intercom failed, AWS S3 error")
    except Exception as e:
        print "\nError: "+str(e)+" in Line number "+str(sys.exc_traceback.tb_lineno)+" for local file\n"
        config.log("\nError: "+str(e)+" in Line number "+str(sys.exc_traceback.tb_lineno)+" for local file\n")
        config.log_error("\nError: "+str(e)+" in Line number "+str(sys.exc_traceback.tb_lineno)+" for local file\n")
        notify_hipchat(config, "Import to Intercom failed, local storage error", "red")
        notify_slack(config, "Import to Intercom failed, local storage error")
        

#Use AWS S3 to get CSV file            
def get_csv_aws_s3(config):
    try:
        conn=S3Connection(config.config_data["aws_access_key"], config.config_data["aws_secret_key"]) #connect to aws s3
        bucket = conn.get_bucket(config.config_data["aws_bucket_name"]) #get bucket
        if config.config_data["select_file_on_latest_time"]: #time based selection
            bucket_list = bucket.list(prefix=config.config_data["aws_folder"], delimiter="/")
            latest=""
            latest_time=None
            for file_key in bucket_list:
                config.log("File "+str(file_key.key))
                if latest_time is None:
                    latest_time=time.strptime(str(file_key.key).split('.')[0].split('/')[-1], "%Y-%m-%dT%H:%M:%S")
                    latest=file_key
                elif latest_time<time.strptime(str(file_key.key).split('.')[0].split('/')[-1], "%Y-%m-%dT%H:%M:%S"):
                    latest_time=time.strptime(str(file_key.key).split('.')[0].split('/')[-1], "%Y-%m-%dT%H:%M:%S")
                    latest=file_key
            if latest=="":
                print "\nError: No file found - check bucket name and file prefix\n"
                config.log("\nError: No file found - check bucket name and file prefix\n")
                config.log_error("\nError: No file found - check bucket name and file prefix\n")
            else:
                print "Newest File is "+str(latest.key)
                config.log("Newest File is "+str(latest.key))
                latest.get_contents_to_filename(config.tmp_file.name)
                if os.path.isfile(config.tmp_file.name):
                    print "CSV file "+str(latest.key).split('/')[-1]+" downloaded"
                    config.log("CSV file "+str(latest.key).split('/')[-1]+" downloaded")
                    config.log("Reading CSV file")
                    read_csv_file(config, config.tmp_file.name, int(config.config_data["intercom_batch_size"]))
                else:
                    print "\nError CSV file missing "+str(latest.key).split('/')[-1]+"\n"
                    config.log("\nError CSV file missing "+str(latest.key).split('/')[-1]+"\n")
                    config.log_error("\nError CSV file missing "+str(latest.key).split('/')[-1]+"\n")
                    notify_hipchat(config, "Import to Intercom failed, AWS S3 error", "red")
                    notify_slack(config, "Import to Intercom failed, AWS S3 error")
        else: #specific file selection
            key=bucket.get_key(config.config_data["aws_folder"]+config.config_data["file_name"])
            key.get_contents_to_filename(config.tmp_file.name)
            if os.path.isfile(config.tmp_file.name):
                print "CSV file "+str(key.key).split('/')[-1]+" downloaded"
                config.log("CSV file "+str(key.key).split('/')[-1]+" downloaded")
                config.log("Reading CSV file")
                read_csv_file(config, config.tmp_file.name, int(config.config_data["intercom_batch_size"]))
            else:
                print "\nError CSV file missing "+str(key.key).split('/')[-1]+"\n"
                config.log("\nError CSV file missing "+str(key.key).split('/')[-1]+"\n")
                config.log_error("\nError CSV file missing "+str(key.key).split('/')[-1]+"\n")
                notify_hipchat(config, "Import to Intercom failed, AWS S3 error", "red")
                notify_slack(config, "Import to Intercom failed, AWS S3 error")
    except Exception as e:
        print "\nError: "+str(e)+" in Line number "+str(sys.exc_traceback.tb_lineno)+" for AWS S3\n"
        config.log("\nError: "+str(e)+" in Line number "+str(sys.exc_traceback.tb_lineno)+" for AWS S3\n")
        config.log_error("\nError: "+str(e)+" in Line number "+str(sys.exc_traceback.tb_lineno)+" for AWS S3\n")
        notify_hipchat(config, "Import to Intercom failed, AWS S3 error", "red")
        notify_slack(config, "Import to Intercom failed, AWS S3 error")

# No. of users imported        
no_of_users_imported=0

#Read CSV file and upload users in batches        
def read_csv_file(config, filename, batch_size=50):
    global no_of_users_imported
    try:
        delimit=config.config_data["csv_delimiter"]
    except Exception as e:
        delimit=","
    if delimit=="":
        delimit=","
    csvReader = csv.reader(open(filename, 'rb'), delimiter=delimit, quotechar='"') #comma delimited file
    data={"users":[]}
    for row in csvReader: #get headers in each column
        header=row
        break
    try:
        i=0
        b=0
        stop=False
        for row in csvReader: #load data in batches and call intercom
            #user={'location_data': {}, 'custom_attributes': {}}  
            user={'custom_attributes': {}}  
            k=0       
            basic_params=config.config_data["basic_params"]
            basic_params_types=config.config_data["basic_params_types"]
            for key, value in basic_params.items():
                try:
                    if "'" in value:
                        value=value.replace("'","")
                    elif value.strip() == "NULL":
                        value=""
                    else:
                        value=row[header.index(value)]
                    try:
                        if basic_params_types[key] == "string":
                            value = str(value)
                        elif basic_params_types[key] == "integer":
                            value = int(value)
                        elif basic_params_types[key] == "timestamp":
                            value = int(value)
                        elif basic_params_types[key] == "boolean":
                            if str(value) == "1":
                                value = True
                            else:
                                value = False
                        else:
                            value = str(value)
                    except Exception as e:
                        try:
                            if basic_params_types[key] == "string":
                                value = ""
                            elif basic_params_types[key] == "integer":
                                value = 0
                            elif basic_params_types[key] == "timestamp":
                                value = 0
                            elif basic_params_types[key] == "boolean":
                                value = False
                            else:
                                value = ""
                        except Exception as e:
                            pass    
                    user[key]=value
                except Exception as e:
                    pass
            custom_attributes=config.config_data["custom_attributes"]
            custom_attributes_types=config.config_data["custom_attributes_types"]
            for key, value in custom_attributes.items():
                try:
                    if "'" in value:
                        value=value.replace("'","")
                    elif value.strip() == "NULL":
                        value="NULL"
                    else:
                        value=row[header.index(value)]
                    try:
                        if custom_attributes_types[key] == "string":
                            value = str(value)
                        elif custom_attributes_types[key] == "integer":
                            value = int(value)
                        elif custom_attributes_types[key] == "timestamp":
                            value = int(value)
                        elif custom_attributes_types[key] == "boolean":
                            if str(value) == "1":
                                value = True
                            else:
                                value = False
                        else:
                            value = str(value)
                    except Exception as e:
                        try:
                            if custom_attributes_types[key] == "string":
                                value = "NULL"
                            elif custom_attributes_types[key] == "integer":
                                value = 0
                            elif custom_attributes_types[key] == "timestamp":
                                value = 0
                            elif custom_attributes_types[key] == "boolean":
                                value = False
                            else:
                                value = "NULL"
                        except Exception as e:
                            pass
                    user["custom_attributes"][key.replace("_", " ")]=value
                except Exception as e:
                   pass
            data["users"].append(user)
            i+=1
            if i%batch_size==0:
                j=0
                halt=True
                while halt:
                    if not intercom(config, data, b): #if Intercom fails, retry 50 times, pause 5 seconds, retry 50 times then quit if still no reply
                        j+=1
                    else:
                        halt=False
                        b+=1
                        del data["users"][:]
                    if j>50:
                        if stop:
                            halt=False
                            print "\nError: \nIntercom API failed\n"
                            config.log("\nError: \Intercom API failed\n")
                            config.log_error("\nError: \nIntercom API failed\n")
                            break
                        time.sleep(5)
                        j=0
                        config.log("Intercom API failed Retrying Intercom API")
                        stop=True
                if stop:
                    break                
        if len(data["users"])>0: #add leftover members after last batch
            j=0
            halt=True
            while halt:
                if not intercom(config, data, b):
                    j+=1
                else:
                    halt=False
                    b+=1
                    del data["users"][:]
                if j>50:
                    if stop:
                        halt=False
                        print "\nError: \Intercom API failed\n"
                        config.log("\nError: \nIntercom API failed\n")
                        config.log_error("\nError: \nIntecom API failed\n")
                        break
                    time.sleep(5)
                    j=0
                    config.log("Intercom API failed Retrying Intercom API")
                    stop=True
        if stop:
            if config.config_data["intercom_bulk_api"]:
                print "\nFailed to complete import to Intercom with "+str(i-batch_size)+" users done\n"
                config.log("\nFailed to complete import to Intercom with "+str(i-batch_size)+" users done\n")
                config.log_error("\nFailed to complete import to Intercom with "+str(i-batch_size)+" users done\n")
                notify_hipchat(config, "Failed to complete import to Intercom with "+str(i-batch_size)+" users done", "red")   
                notify_slack(config, "Failed to complete import to Intercom with "+str(i-batch_size)+" users done")   
            else:                
                print "\nFailed to complete import to Intercom with "+str(no_of_users_imported)+" users done\n"
                config.log("\nFailed to complete import to Intercom with "+str(no_of_users_imported)+" users done\n")
                config.log_error("\nFailed to complete import to Intercom with "+str(no_of_users_imported)+" users done\n")
                notify_hipchat(config, "Failed to complete import to Intercom with "+str(no_of_users_imported)+" users done", "red")   
                notify_slack(config, "Failed to complete import to Intercom with "+str(no_of_users_imported)+" users done")   
        else:
            if config.config_data["intercom_bulk_api"]:
                print "\nImport of "+str(i)+" users to Intercom was successful in "+str(b)+" batches\n"
                config.log("\nImport of "+str(i)+" users to Intercom was successful in "+str(b)+" batches\n")
                notify_hipchat(config, "Import of "+str(i)+" users to Intercom was successful", "green") 
                notify_slack(config, "Import of "+str(i)+" users to Intercom was successful")     
            else:  
                print "\nImport of "+str(no_of_users_imported)+" users to Intercom was successful\n"
                config.log("\nImport of "+str(no_of_users_imported)+" users to Intercom was successful\n")
                notify_hipchat(config, "Import of "+str(no_of_users_imported)+" users to Intercom was successful", "green") 
                notify_slack(config, "Import of "+str(no_of_users_imported)+" users to Intercom was successful")     
    except Exception as e:
        print "\nError: "+str(e)+" in Line number "+str(sys.exc_traceback.tb_lineno)+" for import csv\n"
        config.log("\nError: "+str(e)+" in Line number "+str(sys.exc_traceback.tb_lineno)+" for import csv\n")
        config.log_error("\nError: "+str(e)+" in Line number "+str(sys.exc_traceback.tb_lineno)+" for import csv\n")
        notify_hipchat(config, "Import to Intercom failed", "red")    
        notify_slack(config, "Import to Intercom failed")   

#Method to add/update Intercom users list - POST request - JSON input/output
def intercom(config, data, batch):        
    global no_of_users_imported
    try:
        authinfo = urllib2.HTTPPasswordMgrWithDefaultRealm()
        authinfo.add_password(None, "api.intercom.io" , config.config_data["intercom_api_id"], config.config_data["intercom_api_key"])
        handler = urllib2.HTTPBasicAuthHandler(authinfo)
        myopener = urllib2.build_opener(handler)
        opened = urllib2.install_opener(myopener) 
        base64string = base64.encodestring('%s:%s' % (config.config_data["intercom_api_id"], config.config_data["intercom_api_key"])).replace('\n', '')
        if config.config_data["intercom_bulk_api"]:
            url="https://"+config.config_data["intercom_api_url_bulk_users"]        
            json_data = json.dumps(data) 
            req = urllib2.Request(url, json_data)
            #req.add_header("Authorization", "Basic %s" % base64string)   
            req.add_header('Content-Type', 'application/json')
            req.add_header('Accept', 'application/json')        
            response=urllib2.urlopen(req, timeout=config.config_data["intercom_timeout"])        
            #reply=json.loads(response.read())
            try:
                config.log("Intercom Batch No. "+str(batch+1)+" completed")
                print "Intercom Batch No. "+str(batch+1)+" completed"
                #config.log("Intercom Job Id "+str(reply["id"]))
                #config.log("Intercom Job Link "+str(reply["links"]["self"]))                         
                #config.log("Intercom Job Errors "+str(reply["links"]["error"]))                         
            except Exception as e:
                pass
            return True 
        else:
            url="https://"+config.config_data["intercom_api_url_users"] 
            for user in data["users"]: 
                try:
                    json_data = json.dumps(user)      
                    req = urllib2.Request(url, json_data)
                    #req.add_header("Authorization", "Basic %s" % base64string)   
                    req.add_header('Content-Type', 'application/json')
                    req.add_header('Accept', 'application/json')        
                    response=urllib2.urlopen(req, timeout=config.config_data["intercom_timeout"])        
                    reply=json.loads(response.read())
                    no_of_users_imported+=1
                except urllib2.HTTPError, error: #connection error
                    contents=json.loads(error.read())
                    try:
                        for value in contents["errors"]:
                            error=""
                            try:
                                error+=" | Code:"+str(value["code"])
                            except Exception as e:
                                pass              
                            try:
                                error+=" | Message:"+str(value["message"])
                            except Exception as e:
                                pass                    
                            try:
                                error+=" | Field:"+str(value["field"])
                            except Exception as e:
                                pass                    
                            config.log_error("Intercom Error: "+"Error: "+error)
                    except Exception as e:
                        try:
                            config.log_error("Intercom Error: "+str(json.loads(contents)["errors"]))
                        except Exception as e:                
                            config.log_error("Intercom Error: "+str(contents))            
                    #return False
            try:
                config.log("Intercom Batch No. "+str(batch+1)+" completed")
                print "Intercom Batch No. "+str(batch+1)+" completed"
                #config.log("Intercom Job Id "+str(reply["id"]))
                #config.log("Intercom Job Link "+str(reply["links"]["self"]))                         
                #config.log("Intercom Job Errors "+str(reply["links"]["error"]))                         
            except Exception as e:
                pass
            return True 
    except urllib2.HTTPError, error: #connection error
        contents=json.loads(error.read())
        try:
            for value in contents["errors"]:
                error=""
                try:
                    error+=" | Code:"+str(value["code"])
                except Exception as e:
                    pass              
                try:
                    error+=" | Message:"+str(value["message"])
                except Exception as e:
                    pass                    
                try:
                    error+=" | Field:"+str(value["field"])
                except Exception as e:
                    pass                    
                config.log_error("Intercom Error: "+"Error: "+error)
        except Exception as e:
            try:
                config.log_error("Intercom Error: "+str(json.loads(contents)["errors"]))
            except Exception as e:                
                config.log_error("Intercom Error: "+str(contents))            
        return False
    except Exception as e:
        config.log_error("\nError: "+str(e)+" in Line number "+str(sys.exc_traceback.tb_lineno)+" for Intercom request\n")
        return False

#Method to notify hipchat - POST request - x-www-form-urlencoded input and JSON output    
def notify_hipchat( config, message, color, log_message=None,):
    if config.config_data["notify_hipchat"]:
        try:
            values={"room_id":config.config_data["hipchat_room_id"], "from":config.config_data["hipchat_from"], "message":message, "message_format":"text", "color":color}
            #url="https://api.hipchat.com/v1/rooms/message?auth_token="+config.config_data["hipchat_api_key"]+"&room_id="+config.config_data["hipchat_room_id"]+"&from="+config.config_data["hipchat_from"]+"&message="+message+"&message_format=text&color="+color
            url="https://api.hipchat.com/v1/rooms/message?format=json&auth_token="+config.config_data["hipchat_api_key"]
            data = urllib.urlencode(values)
            #req = urllib2.Request(url) #use commented url and req for get request
            req = urllib2.Request(url, data)
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            response = urllib2.urlopen(req)    
            reply=json.loads(response.read())
            try:
                config.log("Message to hipchat \""+message+"\" "+str(reply["status"]))               
            except KeyError as e:
                config.log("Message to hipchat \""+message+"\" failed")
                config.log_error("Message to hipchat \""+message+"\" failed")
                config.log_error("\nError: "+str(e)+" in Line number "+str(sys.exc_traceback.tb_lineno)+" for hipchat response\n")    
            except Exception as e:
                config.log_error("\nError: "+str(e)+" in Line number "+str(sys.exc_traceback.tb_lineno)+" for hipchat response\n")
        except urllib2.HTTPError as e: #connection error
            error_message = json.loads(e.read())
            config.log_error("\nHipchat Error: "+error_message["error"]["message"]+"\n")    
        except Exception as e:
            config.log_error("\nError: "+str(e)+" in Line number "+str(sys.exc_traceback.tb_lineno)+" for hipchat config request\n")
        

#Method to notify slack - POST request - JSON input and JSON output    
def notify_slack( config, message, log_message=None,):
    if config.config_data["notify_slack"]:
        try:
            values={"text":message,"username":config.config_data["slack_username"],"icon_url":config.config_data["slack_icon_url"],"icon_emoji":config.config_data["slack_icon_emoji"],"channel":config.config_data["slack_channel"]}        
            url=config.config_data["slack_api_incoming_webhook"]
            data = json.dumps(values)            
            req = urllib2.Request(url, data)
            req.add_header('Content-Type', 'application/JSON')
            req.add_header('Accept', 'application/JSON')
            response = urllib2.urlopen(req)    
            reply=response.read()
            try:
                config.log("Message to slack \""+message+"\" "+str(reply))               
            except KeyError as e:
                config.log("Message to slack \""+message+"\" failed")
                config.log_error("Message to slack \""+message+"\" failed")
                config.log_error("\nError: "+str(e)+" in Line number "+str(sys.exc_traceback.tb_lineno)+" for slack response\n")    
        except Exception as e:
            config.log_error("\nError: "+str(e)+" in Line number "+str(sys.exc_traceback.tb_lineno)+" for slack response\n")    
        except urllib2.HTTPError as e: #connection error
            error_message = e.read()
            config.log_error("\Slack Error: "+error_message+"\n")    
        except Exception as e:
            config.log_error("\nError: "+str(e)+" in Line number "+str(sys.exc_traceback.tb_lineno)+" for slack config request\n")
        

if __name__=="__main__":    
    print "\nExport Data Started\n"
    try:
        #Check if filename has been passed as argument and initialize config file data
        config=config_loader.Config_Data(filename=str(sys.argv[1]))
    except Exception as e:
        #If no file argument is present, initialize config data without file name
        config=config_loader.Config_Data()
    #Check for config data validity - validations done upon initialization        
    if config.valid:        
        print "Config data loaded"
        notify_hipchat(config, "Import to Intercom was initiated", "yellow")
        notify_slack(config, "Import to Intercom was initiated")
        #Use AWS or local        
        if config.config_data["use_aws"]:
            get_csv_aws_s3(config)
            tmp_file=config.tmp_file.name
            config.tmp_file.close()
            try:
                os.remove(tmp_file)
            except Exception as e:
                pass
        else:
            pass
            use_local(config)
        #close log files
        config.close_loggers()    
    else:
        print "\nInvalid config\n"    
        
    
    
        
         
             
             
            
        
