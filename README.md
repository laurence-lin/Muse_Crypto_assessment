Muse Assessment: 
Get Crypto-currency real-time data from https://coinmarketcap.com every 10 minutes, and stored into Supabase.


Execution:
airflow webserver
airflow scheduler

This would launch Airflow server to get data from CoinMarketCap every 10 minutes, and upload data into Supabase table 'muse_project'.

Supabase: Cloud Postgres database
Upon insert new data, run function for new query analysis: select latest_crypto_std();

This would update the analysis table 'hourly_analysis', which get the crypto-price updated last 3 hours and calculate the standard-deviation of the currency.
Use 'hourly_analysis' to find out latest most frequent trading currency provided by CoinMarketCap.
