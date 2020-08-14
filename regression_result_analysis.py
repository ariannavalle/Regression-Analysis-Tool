import json
import sys
log = open('log.txt', 'w') 

#Gets all the devices from the .server_config file, it will get everything after the string "DEVICES = " and insert it into a list
def get_server_config_devices(file):
    with open(file) as f:
        for line in f:
            if 'DEVICES = ' in line:
                server_config = line.split(",")
                #  1: prints everything in the list except for the fist item (server_config[0]), since in this case the first item will include the word "DEVICES"
                server_config = server_config[1:] 
        return server_config[1:]
 
#Gets the total number of items in the list in order to display the total number of monitors in the server_config file
def get_device_count():
    ids = get_server_config_devices('.server_config')
    print('There are a total of ' + str(len(ids)) + ' monitors under test.')
    log.write('There are a total of ' + str(len(ids)) + ' monitors under test.\n')

#Receives a file containing a data set of monitors and the amount of times each monitor has ran     
def get_monitors_ran(file):
    try:
        with open(file) as f:
            data = json.load(f)
            length = len(data['results'][0]['series'])
            
            if length > 0:
                results = []
                monitors_that_ran = []
                for x in range(0,length):
                    results = data['results'][0]['series'][x]['tags']['monitor']
                    results = monitors_that_ran.append(results)
        
                print(str(len(monitors_that_ran)) + ' monitors have ran on this version.')
                log.write(str(len(monitors_that_ran)) + ' monitors have ran on this version.\n') 
                return monitors_that_ran
    except: 
        print("No monitors have ran or empty/incorrect data set in file.\n")

#Receives the device list and the monitors that ran (the return value of get_server_config_devices and get_monitors_ran)
#Calculates the percentage of monitors ran dy dividing monitors ran by the list of devices 
#Then returns the list of devices that did not run by subtracting the server_config devices by the monitors ran 
def diff(total_devices, monitors_ran): 
    if (monitors_ran == 'monitors_ran_old_version.json'):
        print('\nOld Version (' + sys.argv[1] + '): \n')
        log.write('\nOld Version (' + sys.argv[1] + '): \n')
    elif (monitors_ran == 'monitors_ran_new_version.json'):
        print('New Version (' + sys.argv[2] + '): \n')
        log.write('New Version (' + sys.argv[2] + '): \n')
    else:
        print('\nVersion not detected')
        log.write('\nVersion not detected')
   
    total_devices = get_server_config_devices(total_devices)
    monitors_ran = get_monitors_ran(monitors_ran)
        
    percentage = (float(len(monitors_ran))/float(len(total_devices)))*100
    print('This represents ' + str(round(percentage,2)) + ' percent of the total set.\n') 
    log.write('This represents ' + str(round(percentage,2)) + ' percent of the total set.\n\n') 
    print(list(set(total_devices) - set(monitors_ran))) 
    return(list(set(total_devices) - set(monitors_ran))) 

#Receives a file containing a data set that includes a monitors, status, and the number of times it has ran with that status.
def failed_runs(file):
    with open(file) as f:
        data = json.load(f)
        length = len(data['results'][0]['series'])
        
        if length > 0:
            failures = []
            for x in range(0,length):
                monitor_id = data['results'][0]['series'][x]['tags']['monitor']
                status_code = data['results'][0]['series'][x]['tags']['status']
                fail_count = data['results'][0]['series'][x]['values'][0][1]
                
                #I'm omitting monitors that have failed once as oftentimes it's a fluke.
                if (fail_count > 1):
                    if (sys.argv[3]=='y'):
                        failures.append((monitor_id,status_code))
                    else :
                        failures.append((monitor_id,0))

            return failures

def eval_failures(old_failures,new_failures):
    version1 = ''
    version2 = ''
    if (old_failures  == 'failed_runs_old.json'):
        version1 = sys.argv[2]
        version2 = sys.argv[1]
    elif (old_failures == 'failed_runs_new.json'):
        version1 = sys.argv[1]
        version2 = sys.argv[2]
    else:
        print('\nVersion not detected')
        
    old_failures = failed_runs(old_failures)
    new_failures = failed_runs(new_failures)

    unique_values = (list(set(new_failures) - set(old_failures)))
    print("The following monitors have detected failures in " + version1 + " that were not present in " + version2 + ": ")
    log.write("The following monitors have detected failures in " + version1 + " that were not present in " + version2 + ": \n")
    
    if (version1 == sys.argv[2]):
        f = open('output.txt','w')
        log.write("('Monitor ID', 'ST code in version " + sys.argv[2] + "')\n")
        for x in range(0,len(unique_values)): 
            if (x == len(unique_values)-1):
                print(unique_values[x][0])
                log.write(str(unique_values[x]) + '\n\n')
                f.write(unique_values[x][0])
            else:
                print(unique_values[x][0])
                log.write(str(unique_values[x]) + ',')
                f.write(unique_values[x][0] + ',')
        f.close()
    elif (version1 == sys.argv[1]):
        f = open('output2.txt','w')
        log.write("('Monitor ID', 'ST code in version " + sys.argv[1] + "')\n")
        for x in range(0,len(unique_values)): 
            if (x == len(unique_values)-1):
                print(unique_values[x][0])
                log.write(str(unique_values[x]) + '\n\n')
                f.write(unique_values[x][0])
            else:
                print(unique_values[x][0])
                log.write(str(unique_values[x]) + ',')
                f.write(unique_values[x][0] + ',')
        f.close()
    else:
        print('\nUnable to detect failed runs.')
    
    return unique_values 
    
get_device_count()
diff('.server_config', 'monitors_ran_old_version.json')
diff('.server_config', 'monitors_ran_new_version.json')
eval_failures('failed_runs_old.json','failed_runs_new.json')
eval_failures('failed_runs_new.json','failed_runs_old.json')
log.close()