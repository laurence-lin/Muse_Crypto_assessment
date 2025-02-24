create or replace function latest_crypto_std()
returns void as $$
declare 
  result_row record; 
begin
  for result_row in 
      select 
      crypto_name, round(STDDEV_SAMP(price), 10) standard_deviation
    from muse_project
    where update_time > now() - interval '3 hours'
    group by crypto_name
    limit 10
  loop 
    insert into hourly_analysis (crypto_name, standard_deviation)
    values (result_row.crypto_name, result_row.standard_deviation)
    on conflict (crypto_name) do update
    set standard_deviation = result_row.standard_deviation;
  end loop;

end;
$$ language plpgsql;