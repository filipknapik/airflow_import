# Import Airflow environment to Cloud Composer

This tool importing existing Airflow environment into Cloud Composer. 

The tool imports the following components of Airflow configurations:
- User-created connections
- Connections with passwords are automatically converted into Secrets in Google Secret Manager - thus improving security of the deployment
- Environment Variables (WORK IN PROGRESS)
- PyPI modules (WORK IN PROGRESS)
- DAGs (WORK IN PROGRESS)
- Plugins (WORK IN PROGRESS)

The script generates a set of scripts that, once triggered, will create and configure Cloud Composer environment. Creation of Cloud Composer environments is implemented through TerraForm. 

WORK IN PROGRESS.....