import requests
import pandas as pd
from datetime import timedelta
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

TOP_1M_DOMAINS = 'https://storage.yandexcloud.net/kc-startda/top-1m.csv'
TOP_1M_DOMAINS_FILE = 'top-1m.csv'


def get_data():
    # Здесь пока оставили запись в файл, как передавать переменую между тасками будет в третьем уроке
    top_doms = pd.read_csv(TOP_1M_DOMAINS)
    top_data = top_doms.to_csv(index=False)

    with open(TOP_1M_DOMAINS_FILE, 'w') as f:
        f.write(top_data)

def get_top_10_domain_zones():
    df = pd.read_csv(TOP_1M_DOMAINS_FILE, names=['rank', 'domain'])
    df['domain_zone'] = df['domain'].apply(lambda x: x.split('.')[-1])
    top_10_domain_zones = df['domain_zone'].value_counts().reset_index().head(10)
    with open('top_10_domain_zones.csv', 'w') as f:
        f.write(top_10_domain_zones.to_csv(index=False, header=False))
        
def get_longest_name_domain():
    df = pd.read_csv(TOP_1M_DOMAINS_FILE, names=['rank', 'domain'])
    df['lenght_domain'] = df.domain.str.len()
    longest_name_domain = df.sort_values('lenght_domain',ascending=False)['domain'].head(1).values[0]
    with open('longest_name_domain.txt', 'w') as f:
        f.write(longest_name_domain) 

def get_rank_airflow():
    try:
        df = pd.read_csv(TOP_1M_DOMAINS_FILE, names=['rank', 'domain'])
        airflow_rank = str(df[df.domain == 'airflow.com']['rank'].values[0])
    except IndexError:
        airflow_rank = 'Домен отсутствует'
        
    with open('airflow_com.txt', 'w') as f:
        f.write(airflow_rank)    


def print_data(ds):
    with open('top_10_domain_zones.csv', 'r') as f:
        top_10_domain_zones = f.read()
    with open('longest_name_domain.txt', 'r') as f:
        longest_name_domain = f.read()
    with open('airflow_com.txt', 'r') as f:
        airflow_com = f.read()
    
    date = ds

    print(f'Top 10 domains for date {date}')
    print(top_10_domain_zones)

    print(f'The longest domain for date {date}')
    print(longest_name_domain)
    
    print(f'Rank airflow.com for date {date}')
    print(airflow_com)


default_args = {
    'owner': 'd-alekseev-38',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2023, 7, 10),
}
schedule_interval = '0 12 * * *'

dag = DAG('lesson_2_d-alekseev-38', default_args=default_args, schedule_interval=schedule_interval)

t1 = PythonOperator(task_id='get_data',
                    python_callable=get_data,
                    dag=dag)

t2 = PythonOperator(task_id='get_top_10_domain_zones',
                    python_callable=get_top_10_domain_zones,
                    dag=dag)

t3 = PythonOperator(task_id='get_longest_name_domain',
                    python_callable=get_longest_name_domain,
                    dag=dag)

t4 = PythonOperator(task_id='get_rank_airflow',
                        python_callable=get_rank_airflow,
                        dag=dag)

t5 = PythonOperator(task_id='print_data',
                    python_callable=print_data,
                    dag=dag)

t1 >> [t2, t3, t4] >> t5
