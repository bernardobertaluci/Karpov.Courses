import pandas as pd
from datetime import timedelta
from datetime import datetime

from airflow.decorators import dag, task

Path_file = '/var/lib/airflow/airflow.git/dags/a.batalov/vgsales.csv'

default_args = {
    'owner': 'd-alekseev-38',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2023, 7, 12)
}

login = 'd-alekseev-38'
target_year = 1994 + hash(f'{login}') % 23


@dag(default_args=default_args, schedule_interval='0 12 * * *', catchup=False)
def vgsales_airflow_2_d_alekseev_38():
    @task()
    def get_data_target_year():
        vgsales = pd.read_csv(Path_file)
        vgsales_target_year = vgsales[vgsales.Year == target_year]
        return vgsales_target_year

    @task()
    def get_best_selling(vgsales_target_year):
        top_game = vgsales_target_year.nlargest(1, 'Global_Sales')
        game_name = top_game['Name'].values[0]
        sales_count = top_game['Global_Sales'].values[0]
        return {'game_name': game_name, 'sales_count': sales_count}

    @task()
    def get_best_genre_europe(vgsales_target_year):
        genre_sales_europe = vgsales_target_year.groupby('Genre')['EU_Sales'].sum()
        sorted_genre_sales_europe = genre_sales_europe.sort_values(ascending=False)
        best_genre_europe = sorted_genre_sales_europe.head(1).idxmax()
        return best_genre_europe

    @task()
    def get_na_sales(vgsales_target_year):
        filtered_df = vgsales_target_year[vgsales_target_year['NA_Sales'] > 1]
        platform_counts = filtered_df['Platform'].value_counts()
        top_platform = platform_counts.idxmax()
        return top_platform

    @task()
    def get_avg_sales_japan(vgsales_target_year):
        publisher_sales = vgsales_target_year.groupby('Publisher')['JP_Sales'].mean()
        top_publisher = publisher_sales.idxmax()
        return top_publisher

    @task()
    def get_count_games_better_europe_than_japan(vgsales_target_year):
        better_sales_count = (vgsales_target_year['EU_Sales'] > vgsales_target_year['JP_Sales']).sum()
        return better_sales_count

    @task()
    def print_data(best_selling, best_genre_europe, na_sales, avg_sales_japan, count_games_better_europe_than_japan):
        game_name, sales_count = best_selling['game_name'], best_selling['sales_count']

        print(f'''Самая продаваемая игра в {target_year} году
                  была {game_name} в колисчестве {sales_count} млн экземпляров''')

        print(f'''Самые продаваемый жанр в {target_year} году
                          был {best_genre_europe}''')

        print(f'''Платформа на которой продалось игр более,
                  чем миллионым тиражом в Северной Америке в {target_year} году
                  была {na_sales}''')

        print(f'''Издатель у которого самые высокие средние продажи в Японии в {target_year} году
                  является {avg_sales_japan}''')

        print(f'''Количество игр в {target_year} году, которые продались лучше в Европе, чем в Японии
                  равняется {count_games_better_europe_than_japan}''')

    data_target_year = get_data_target_year()
    best_selling = get_best_selling(data_target_year)
    best_genre_europe = get_best_genre_europe(data_target_year)
    na_sales = get_na_sales(data_target_year)
    avg_sales_japan = get_avg_sales_japan(data_target_year)
    count_games_better_europe_than_japan = get_count_games_better_europe_than_japan(data_target_year)

    print_data(best_selling, best_genre_europe, na_sales, avg_sales_japan, count_games_better_europe_than_japan)


vgsales_airflow_2_d_alekseev_38 = vgsales_airflow_2_d_alekseev_38()
