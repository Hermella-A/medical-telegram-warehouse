SELECT *
FROM fct_messages
WHERE date_key > (SELECT MAX(date_key) FROM dim_dates)