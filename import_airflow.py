import os, subprocess, json, re
import shutil
import configparser


skip_connections = ['kylin_default', 'local_mysql', 'postgres_default', 'tableau_default']

secretsFolder = "secrets"
connections = []
configs = []
bashScript = []
TFScript = []



def loadConfig():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'settings.cfg'))
    return config

def deleteSecrets(secretsPath):
    try:
        shutil.rmtree(secretsPath)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))

def importConnections(secretsPath):
    global connections
    getConnections = "airflow connections list -o json"

    proc = subprocess.Popen([getConnections], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    if proc.returncode != 0:
        exit(1)         # Stop execution if connections listing didn't succeed
    responseColored = out.decode("utf-8")               # 
    formatter = re.compile(r'\x1b[^m]*m')               # Compile formatting rule as 
    connectionsClean = formatter.sub('', responseColored)    # 

    try:
        connArray = json.loads(connectionsClean)
    except:
        print("Error loading connections")
        exit(1)

    for conn in connArray:
        if conn['password']:
            if conn['conn_id'] not in skip_connections:
                connections.append({"conn_id": conn['conn_id'], "uri": conn['get_uri']})
        else:
            pass

    try: 
        os.mkdir(secretsPath) 
    except OSError as error: 
        print(error)      

    if len(connections)>0:
        bashScript.append("gcloud services enable secretmanager.googleapis.com")
        configs.append({"section": "secrets", "key": "backend", "value": "airflow.providers.google.cloud.secrets.secret_manager.CloudSecretManagerBackend"})
        for connection in connections:
            if 'uri' in connection:
                bashScript.append("gcloud secrets create airflow-connections-" + connection['conn_id'] + " --replication-policy=\"automatic\"")
                with open(os.path.join(secretsPath,connection['conn_id']), "w") as myfile:
                    try:
                        myfile.write(connection['uri'])
                    except:
                        print("Error writing secret to a file")
                bashScript.append("gcloud secrets versions add airflow-connections-" + connection['conn_id'] + " --data-file="+os.path.join(secretsPath,connection['conn_id']))   

    for line in bashScript:
        print(line)
        proc = subprocess.Popen([line], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        if proc.returncode != 0:
            deleteSecrets(secretsPath)
            exit(1)                                 # Stop execution if connections listing didn't succeed
    
    deleteSecrets(secretsPath)

def main():
    secretsPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), secretsFolder)
    config = loadConfig()
    
    bashScript.append("gcloud config set project " + config['google_cloud']['project'])

    if config['features'].getboolean('connections'):
        importConnections(secretsPath)

    

if __name__ == "__main__":
    main()
