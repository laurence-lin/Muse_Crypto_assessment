from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.models.taskinstance import TaskInstance
import logging
from airflow.operators.python import get_current_context
from airflow.decorators import task
import pytz



local_tz = pytz.timezone('Asia/Taipei') # example of using Taipei TimeZone
now_local = datetime.now(local_tz) - timedelta(days=1)
now_utc = now_local.astimezone(pytz.utc)


# 所有工作都可以分享這一套設定
default_args = {
    'owner': 'laurence', # Owner of the job
    'retries': 1, # Upper limit of failed times before retry
    'retry_delay': timedelta(seconds=5), # Wait time before job start
    'start_date': now_utc, # Start date of job launch
  	'sla': timedelta(seconds=5), # Expected time cost to run the job, if exceeds then send alert mail
  	'execution_timeout': timedelta(minutes=5), # If timeout for a job, stop this job
    'do_xcom_push': True, # Pass the status of this job to other jobs
}


python_dir = "/mnt/c/Users/User/laurence/Muse_assessment/muse_env/bin/python3"
extract_py = "/mnt/c/Users/User/laurence/Muse_assessment/src/extract_crypto.py"

with DAG(
    'muse_dag', # Name of DAG
    description = 'Muse DAG assessment to gather data', # Description shown in UI
    schedule="*/10 * * * *",
    default_args=default_args,
    tags = ["Muse_DAG"],
    catchup = False,
) as dag:

    
    start = EmptyOperator(task_id = 'start')
    etl_task = BashOperator(task_id = "extract_crypto_data",
                          bash_command="{} {}".format(python_dir, extract_py))
    end = EmptyOperator(task_id = 'end')
    
    # define relationship btw tasks
    start >> etl_task >> end  


