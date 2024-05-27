-- SQL script that creates an index idx_name_first 
CREATE INDEX idx_name_first_score
ON names(name(1), score);
