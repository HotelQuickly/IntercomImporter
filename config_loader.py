#import for os file/directory management
import os
#import for system functions
import sys
#import for regular expressions
import re
#import for time class
import time
#class for config file data as object
class Config_Data:
    #constructor
    def __init__(self, configfilename="config", delimiter='=', filename=None):
        self.configfilename=configfilename   
        try:
            #get data from config file
            if isinstance(self.configfilename, basestring):    
                if os.path.isfile(self.configfilename):
                    config_file=open(self.configfilename,'r')
                    print "Config file located - "+self.configfilename
                    i=0
                    self.config_data=dict()
                    for line in config_file:
                        line.strip(' \t\n\r')
                        if not line[0]=="#" and not len(line)==0 and line.count(delimiter)==1:
                            tmp=line.split(delimiter)
                            if len(tmp)==2:
                                self.config_data[tmp[0].strip(' \t\n\r')]=re.findall('"([^"]*)"', tmp[1])[0]
                            else:
                                print "Invalid line in config file\nLine number "+str(i+1)+"\nLine text \""+line+"\"\nPlease check for excess whitespaces if the line is correct\n"
                                break
                            i+=1      
                    config_file.close()
                    #validate logging settings
                    self.validate_log()
                    self.log("Log Started")
                    #validate AWS/Local usage
                    try:
                        if self.config_data["use_aws"].lower()=="true":
                            self.config_data["use_aws"]=True
                            self.log("AWS S3 in use")
                            self.valid=True
                        else:
                            self.config_data["use_aws"]=False
                            self.log("Local Storage in use")
                            self.valid=True
                    except KeyError as e:
                        print "\nError: AWS/Local storage selection is missing in config\n"
                        self.log("\nError: AWS/Local storage selection is missing in config\n")
                        self.log_error("\nError: AWS/Local storage selection is missing in config\n")
                        self.valid=False
                    if self.valid:
                        #validate AWS/local settings
                        self.validate_aws_local()
                        if self.valid:
                            self.log("Validated Storage Info")
                            #validate file selection settings -  based on time format named files and specific filenames
                            try:
                                if self.config_data["select_file_on_latest_time"].lower()=="true":
                                    self.config_data["select_file_on_latest_time"]=True
                                    self.log("File selection based on time")
                                else:
                                    self.config_data["select_file_on_latest_time"]=False
                                    self.log("File Selection based on filename")                                    
                                    if not filename is None:
                                        self.config_data["file_name"]==str(filename)
                                    if not self.config_data["use_aws"] and os.path.isfile(self.config_data["local_folder"]+self.config_data["file_name"]):
                                        self.log("CSV file is "+self.config_data["local_folder"]+self.config_data["file_name"])
                                    elif not self.config_data["use_aws"]:
                                        self.log("CSV file "+self.config_data["local_folder"]+self.config_data["file_name"]+" not found")
                                        self.log_error("CSV file "+self.config_data["local_folder"]+self.config_data["file_name"]+" not found")
                                        self.valid=False
                            except KeyError as e:
                                print "\nError: No file selection preference found in config\n"
                                self.log("\nError: No file selection preference found in config\n")
                                self.log_error("\nError: No file selection preference found in config\n")
                                self.valid=False
                            #validate csv delimiter and intercom parameter mapping
                            self.validate_csv_settings()
                            if self.valid:
                                self.log("Validated CSV file settings")
                                #validate intercom settings
                                self.validate_intercom()
                                if self.valid:
                                    self.log("Validated Intercom settings")
                                    #validate hipchat settings
                                    self.validate_hipchat()
                else:
                    print "\nError: File "+configfilename+" does not exist\n"
                    self.valid=False
            else:
                print "\nError: File name should be a string\n"
                self.valid=False
        except Exception as e:  
            print "\nError: "+str(e)+" in Line number "+str(sys.exc_traceback.tb_lineno)+"\n"
            self.valid=False
    #slack validation        
    def validate_slack(self):
        try:
            if self.config_data["notify_slack"]=="true":
                self.config_data["notify_slack"]=True
                self.log("Slack notification is enabled")
                try:
                    if self.config_data["slack_api_incoming_webhook"]=="":
                        print "\nError: Slack API Incoming webhook is empty in config\n"
                        self.log("\nError: Slack API Incoming webhook is empty in config\n")
                        self.log_error("\nError: Slack API Incoming webhook is empty in config\n")
                        self.valid=False
                except KeyError as e:
                    print "\nError: Slack API Incoming webhook is missing from config\n"
                    self.log("\nError: Slack API Incoming webhook is missing from config\n")
                    self.log_error("\nError: Slack API Incoming webhook is missing from config\n")
                    self.valid=False
                try:
                    if self.config_data["slack_username"]=="":
                        pass
                except KeyError as e:
                    self.config_data["slack_username"] = ""
                try:
                    if self.config_data["slack_icon_url"]=="":
                        pass
                except KeyError as e:
                    self.config_data["slack_icon_url"] = ""
                try:
                    if self.config_data["slack_icon_emoji"]=="":
                        pass
                except KeyError as e:
                    self.config_data["slack_icon_emoji"] = ""
                
            else:
                self.config_data["notify_slack"]=False
                self.log("Slack notification is disabled")
        except KeyError as e:
            self.valid = False
            print "\nError: notify_slack is empty in config\n"
            self.log("\nError: notify_slack is empty in config\n")
            self.log_error("\nError: notify_slack is empty in config\n")
    #hipchat validation        
    def validate_hipchat(self):
        if self.config_data["notify_hipchat"]=="true":
            self.config_data["notify_hipchat"]=True
            self.log("Hipchat notification is enabled")
            try:
                if self.config_data["hipchat_api_key"]=="":
                    print "\nError: Hipchat API key is empty in config\n"
                    self.log("\nError: Hipchat API key is empty in config\n")
                    self.log_error("\nError: Hipchat API key is empty in config\n")
                    self.valid=False
            except KeyError as e:
                print "\nError: Hipchat API key is missing from config\n"
                self.log("\nError: Hipchat API key is missing from config\n")
                self.log_error("\nError: Hipchat API key is missing from config\n")
                self.valid=False
            try:
                if self.config_data["hipchat_room_id"]=="":
                    print "\nError: Hipchat Room Id is empty in config\n"
                    self.log("\nError: Hipchat Room Id is empty in config\n")
                    self.log_error("\nError: Hipchat Room Id is empty in config\n")
                    self.valid=False
            except KeyError as e:
                print "\nError: Hipchat Room Id is missing from config\n"
                self.log("\nError: Hipchat Room Id is missing from config\n")
                self.log_error("\nError: Hipchat Room Id key is missing from config\n")
                self.valid=False
            try:
                if self.config_data["hipchat_api_url"]=="":
                    self.log("Hipchat API URL is empty in config - using default URL https://api.hipchat.com/v1/")
                    self.config_data["hipchat_api_url"]="https://api.hipchat.com/v1/"
                else:
                    if not self.config_data["hipchat_api_url"][-1]=="/":
                        self.config_data["hipchat_api_url"]=self.config_data["hipchat_api_url"]+"/"
                    self.log("Hipchat API URL is "+self.config_data["hipchat_api_url"])
            except KeyError as e:
                self.log("Hipchat API URL is missing from config - using default URL https://api.hipchat.com/v1/")
                self.config_data["hipchat_api_url"]="https://api.hipchat.com/v1/"
        else:
            self.config_data["notify_hipchat"]=False
            self.log("Hipchat notification is disabled")
    #Intercom validation        
    def validate_intercom(self):
        try:
            if self.config_data["intercom_api_id"]=="":
                print "\nError: Intercom API id is empty in config\n"
                self.log("\nError: Intercom API id is empty in config\n")
                self.log_error("\nError: Intercom API id is empty in config\n")
                self.valid=False
        except KeyError as e:
            print "\nError: Intercom API id is missing from config\n"
            self.log("\nError: Intercom API id is missing from config\n")
            self.log_error("\nError: Intercom API id is missing from config\n")
            self.valid=False
        try:
            if self.config_data["intercom_api_key"]=="":
                print "\nError: Intercom API Key is empty in config\n"
                self.log("\nError: Intercom API Key is empty in config\n")
                self.log_error("\nError: Intercom API Key is empty in config\n")
                self.valid=False
        except KeyError as e:
            print "\nError: Intercom API Key is missing from config\n"
            self.log("\nError: Intercom API Key is missing from config\n")
            self.log_error("\nError: Intercom API Key is missing from config\n")
            self.valid=False
        try:
            if self.config_data["intercom_api_url_bulk_users"]=="":
                self.log("Intercom API users URL is empty in config - using default URL api.intercom.io/users/bulk/")
                self.config_data["intercom_api_url_bulk_users"]="api.intercom.io/users/bulk/"
            else:
                if not self.config_data["intercom_api_url_bulk_users"][-1]=="/":
                    self.config_data["intercom_api_url_bulk_users"]=self.config_data["intercom_api_url_bulk_users"]+"/"
                self.log("Intercom API users URL is "+self.config_data["intercom_api_url_bulk_users"])
        except KeyError as e:
            self.log("Intercom API users URL is missing from config - using default URL api.intercom.io/users/bulk/")
            self.config_data["intercom_api_url_bulk_users"]="api.intercom.io/users/bulk/"
        self.convert_to_int()
    #CSV file settings - Intercom parameters mapping
    def validate_csv_settings(self):
        try:
            self.config_data["basic_params"] = self.config_data["basic_params"].replace(" ", "")
            self.config_data["basic_params"] = self.config_data["basic_params"].replace("{", "")
            self.config_data["basic_params"] = self.config_data["basic_params"].replace("}", "")
            self.config_data["basic_params"] = self.config_data["basic_params"].split(',')
            tmp = dict() 
            for param in self.config_data["basic_params"]:
                try:
                    param = param.split(":")
                    tmp[param[0]] = param[1]
                except Exception as e:    
                    self.valid=False        
                    self.log_error("\nError: Invalid basic params in Intercom parameter mapping - check with example format\n")  
                    break
            self.config_data["basic_params"] = tmp
        except KeyError as e:
            self.valid=False
            self.log_error("\nError: basic params missing in Intercom parameter mapping in config\n")  
        try:
            self.config_data["basic_params_types"] = self.config_data["basic_params_types"].replace(" ", "")
            self.config_data["basic_params_types"] = self.config_data["basic_params_types"].replace("{", "")
            self.config_data["basic_params_types"] = self.config_data["basic_params_types"].replace("}", "")
            self.config_data["basic_params_types"] = self.config_data["basic_params_types"].split(',')
            tmp = dict() 
            for param in self.config_data["basic_params_types"]:
                try:
                    param = param.split(":")
                    tmp[param[0]] = param[1]
                except Exception as e:    
                    self.valid=False        
                    self.log_error("\nError: Invalid basic params Types in Intercom parameter mapping - check with example format\n")  
                    break
            self.config_data["basic_params_types"] = tmp
        except KeyError as e:
            self.valid=False
            self.log_error("\nError: basic params Types missing in Intercom parameter mapping in config\n")  
        try:
            self.config_data["custom_attributes"] = self.config_data["custom_attributes"].replace(" ", "")
            self.config_data["custom_attributes"] = self.config_data["custom_attributes"].replace("{", "")
            self.config_data["custom_attributes"] = self.config_data["custom_attributes"].replace("}", "")
            self.config_data["custom_attributes"] = self.config_data["custom_attributes"].split(',')
            tmp = dict() 
            for param in self.config_data["custom_attributes"]:
                try:
                    param = param.split(":")
                    tmp[param[0]] = param[1]
                except Exception as e:    
                    self.valid=False        
                    self.log_error("\nError: Invalid custom attributes in Intercom parameter mapping - check with example format\n")  
                    break
            self.config_data["custom_attributes"] = tmp
        except KeyError as e:
            self.valid=False
            self.log_error("\nError: custom attributes missing in Intercom parameter mapping in config\n")  
        try:
            self.config_data["custom_attributes_types"] = self.config_data["custom_attributes_types"].replace(" ", "")
            self.config_data["custom_attributes_types"] = self.config_data["custom_attributes_types"].replace("{", "")
            self.config_data["custom_attributes_types"] = self.config_data["custom_attributes_types"].replace("}", "")
            self.config_data["custom_attributes_types"] = self.config_data["custom_attributes_types"].split(',')
            tmp = dict() 
            for param in self.config_data["custom_attributes_types"]:
                try:
                    param = param.split(":")
                    tmp[param[0]] = param[1]
                except Exception as e:    
                    self.valid=False        
                    self.log_error("\nError: Invalid custom attributes Types in Intercom parameter mapping - check with example format\n")  
                    break
            self.config_data["custom_attributes_types"] = tmp
        except KeyError as e:
            self.valid=False
            self.log_error("\nError: custom attributes Types missing in Intercom parameter mapping in config\n")  
        #try:
        #    self.config_data["location_data"] = self.config_data["location_data"].replace(" ", "")
        #    self.config_data["location_data"] = self.config_data["location_data"].replace("{", "")
        #    self.config_data["location_data"] = self.config_data["location_data"].replace("}", "")
        #    self.config_data["location_data"] = self.config_data["location_data"].split(',')
        #    tmp = dict() 
        #    for param in self.config_data["location_data"]:
        #        try:
        #            param = param.split(":")
        #            tmp[param[0]] = param[1]
        #        except Exception as e:    
        #            self.valid=False        
        #            self.log_error("\nError: Invalid location_data in Intercom parameter mapping  - check with example format\n")  
        #            break
        #   self.config_data["location_data"] = tmp
        #except KeyError as e:
        #    self.valid=False
        #    self.log_error("\nError: location_data missing in Intercom parameter mapping in config\n")  
        try:
            if self.config_data["csv_delimiter"]=="":
                self.config_data["csv_delimiter"]=","
        except KeyError as e:
            self.config_data["csv_delimiter"]=","  
    #validate AWS/Local settings        
    def validate_aws_local(self):
        if self.config_data["use_aws"]:
            try:
                if self.config_data["aws_access_key"]=="":
                    print "\nError: AWS S3 Access key is empty in config\n"
                    self.log("\nError: AWS S3 Access key is empty in config\n")
                    self.log_error("\nError: AWS S3 Access key is empty in config\n")
                    self.valid=False
            except KeyError as e:
                print "\nError: AWS S3 Access key is missing from config\n"
                self.log("\nError: AWS S3 Access key is missing from config\n")
                self.log_error("\nError: AWS S3 Access key is missing from config\n")
                self.valid=False
            try:
                if self.config_data["aws_secret_key"]=="":
                    print "\nError: AWS S3 Secret key is empty in config\n"
                    self.log("\nError: AWS S3 Secret key is empty in config\n")
                    self.log_error("\nError: AWS S3 Secret key is empty in config\n")
                    self.valid=False
            except KeyError as e:
                print "\nError: AWS S3 Secret key is missing from config\n"
                self.log("\nError: AWS S3 Secret key is missing from config\n")
                self.log_error("\nError: AWS S3 Secret key is missing from config\n")
                self.valid=False
            try:
                if self.config_data["aws_bucket_name"]=="":
                    print "\nError: AWS S3 bucket name is empty in config\n"
                    self.log("\nError: AWS S3 bucket name is empty in config\n")
                    self.log_error("\nError: AWS S3 bucket name is empty in config\n")
                    self.valid=False
            except KeyError as e:
                print "\nError: AWS S3 bucket name is missing in config\n"
                self.log("\nError: AWS S3 bucket name is missing in config\n")
                self.log_error("\nError: AWS S3 bucket name is missing in config\n")
                self.valid=False
            try:
                if self.config_data["aws_folder"]=="":
                    self.log("\nError: AWS S3 Folder is empty in config - search will be done directly in bucket\n")
            except KeyError as e:
                self.config_data["aws_folder"]=""
                self.log("\nError: AWS S3 Folder is missing in config - search will be done directly in bucket\n")
            try:
                if self.config_data["aws_local_tmp_folder"]=="":                    
                    self.log("Temp folder empty -  default OS provided one will be used")
                    import tempfile
                    self.tmp_file=tempfile.NamedTemporaryFile()
                else:
                    try:
                        folder=self.config_data["aws_local_tmp_folder"]
                        if not folder[-1]=="/":
                            folder+="/"
                        if not os.path.exists(folder):
                            os.makedirs(folder)                        
                        elif not os.path.isdir(folder):
                            os.makedirs(folder)                            
                        self.tmp_file=open(folder+time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+"_tmp.csv", 'wb')    
                    except IOError as e:
                        print "\nError in temp file allocation for AWS S3 download\n"
                        self.log("\nError in temp file allocation for AWS S3 download\n")
                        self.log_error("\nError in temp file allocation for AWS S3 download\n")
                        self.log_error(str(e))
                        self.valid=False
            except KeyError as e:
                self.log("Temp folder empty -  default OS provided one will be used")
                import tempfile
                self.tmp_file=tempfile.NamedTemporaryFile()
        else:
            try:
                if self.config_data["local_folder"]=="":
                    self.log("\nWarning: Local folder for CSV file location is empty in config - using current directory\n")                    
                    self.log_error("\nWarning: Local folder for CSV file location is empty in config\n")
                else:
                    folder=self.config_data["local_folder"]
                    if not os.path.exists(folder):
                        self.log("\nWarning: Local folder for CSV file location does not exist "+folder+" - using current directory\n")
                        self.log_error("\nWarning: Local folder for CSV file location does not exist "+folder+" - using current directory\n")
                        self.config_data["local_folder"]=""
                    elif not os.path.isdir(folder):
                        self.log("\nWarning: Local folder for CSV file location does not exist "+folder+" - using current directory\n")
                        self.log_error("\nWarning: Local folder for CSV file location does not exist "+folder+" - using current directory\n")
                        self.config_data["local_folder"]=""
                    elif not folder[-1]=="/":                        
                        self.config_data["local_folder"]=folder+"/"
                        self.log("Local Folder for CSV file is "+folder)
            except KeyError as e:
                print "\nWarning: Local folder for CSV file location is missing from config - using current directory\n"
                self.log("\nWarning: Local folder for CSV file location is missing from config - using current directory\n")
                self.log_error("\nWarning: Local folder for CSV file location is missing from config - using current directory\n")
                self.config_data["local_folder"]=""
    #validate logging settings            
    def validate_log(self):
        try:
            if self.config_data["output_log"].lower()=="true":
                self.config_data["output_log"]=True
                print "Logging Enabled"
                try:
                    if self.config_data["log_folder"]=="":
                        self.config_data["log_folder"]="log/"
                        print "No log folder has been specified - a log folder will be created in the current folder"   
                except KeyError as e:
                    self.config_data["log_folder"]="log/"
                    print "No log folder has been specified - a log folder will be created in the current folder"
                log_files=self.open_log_file(self.config_data["log_folder"])
                if log_files is None:
                    self.config_data["output_log"]=False
                else:
                    self.logger=log_files
            else:
                self.config_data["output_log"]=False
                print "Logging disabled"
        except KeyError as e:
            print "\nLog output selection is missing - no log will be recorded\n"
            self.config_data["output_log"]=False
        self.do_log=self.config_data["output_log"]
    #open timestamped log files initially    
    def open_log_file(self, folder):           
        try:
            if not folder[-1]=="/":
                folder+="/"
            if not os.path.exists(folder):
                os.makedirs(folder)
            elif not os.path.isdir(folder):
                os.makedirs(folder)
            return open(folder+time.strftime("%Y-%m-%dT%H-%M-%S", time.localtime())+"_debug.log", 'wb'), open(folder+time.strftime("%Y-%m-%dT%H-%M-%S", time.localtime())+"_error.log", 'wb')
        except IOError as e:
            print "Log file creation in "+folder+" "+str(e)
            return None
    #close log files at end    
    def close_loggers(self):           
        try:
            if self.config_data["output_log"]:
                self.log("Log ended")
                self.logger[0].close()
                self.logger[1].close()
        except IOError as e:
            print "Log file error "+folder+" "+str(e)
    #log with timestamp in debug log - log message is flushed onto disk immediately        
    def log(self, message):
        if self.do_log:
            self.logger[0].write(time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" "+message+"\r\n")
            self.logger[0].flush()
    #log error with timestamp in error log - log message is flushed onto disk immediately                    
    def log_error(self, message):
        if self.do_log:
            self.logger[1].write(time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())+" "+message+"\r\n")
            self.logger[1].flush()
    #convert integer strings from config file to integers        
    def convert_to_int(self):
        converted=True
        try:
            self.config_data["intercom_batch_size"]=int(self.config_data["intercom_batch_size"].strip(' \t\r\n'))
            self.log("Intercom batch size is "+str(self.config_data["intercom_batch_size"]))
        except KeyError as e:
            self.config_data["intercom_batch_size"]=50
            self.log("Intercom batch size is missing - using default value 50")
        except Exception as e:
            self.config_data["intercom_batch_size"]=50
            self.log("Intercom batch size is not an integer - using default value 50")     
        try:
            self.config_data["intercom_timeout"]=int(self.config_data["intercom_timeout"].strip(' \t\r\n'))
            self.log("Intercom timeout is "+str(self.config_data["intercom_timeout"]))
        except KeyError as e:
            self.config_data["intercom_timeout"]=30
            self.log("Intercom timeout is missing - using default value 30")
        except Exception as e:
            self.config_data["intercom_timeout"]=30
            self.log("Intercom timeout is not an integer - using default value 30")     
            
    #check if config file is valid        
    def validate(self):
        if self.valid:
            return True
        else:
            return False
