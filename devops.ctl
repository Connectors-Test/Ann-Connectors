LOAD DATA
INFILE 'C:\Users\Krupa\Downloads\devops.csv'
INTO TABLE devops_metrics
APPEND
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  metric_date       DATE "YYYY-MM-DD",
  total_builds      INTEGER EXTERNAL,
  successful_builds INTEGER EXTERNAL,
  failed_tests      INTEGER EXTERNAL,
  deployments       INTEGER EXTERNAL,
  mttr_mins         INTEGER EXTERNAL,
  active_builds     INTEGER EXTERNAL,
  code_coverage_pct FLOAT EXTERNAL,
  commits           INTEGER EXTERNAL,
  open_prs          INTEGER EXTERNAL,
  rollback_events   INTEGER EXTERNAL
)
