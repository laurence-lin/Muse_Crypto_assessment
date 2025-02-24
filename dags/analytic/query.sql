-- Update largest standard deviation in price within last 3 hours
select 
	crypto_name, round(STDDEV_SAMP(price), 10) standard_deviation
from muse_project
where update_time > now() - interval '3 hours'
group by crypto_name
order by standard_deviation desc
;