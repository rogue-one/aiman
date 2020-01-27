## Postgres Data Auditor.  

## How to install

 * clone this repo:
   `git clone git@github.com:rogue-one/aiman.git`
   
 * create virtualenv:
    create a virtualenv to setup the python run-time. This project requires Python 3. The --python= switch must point to
    valid python 3 binary.
    `virtualenv --python=/usr/local/bin/python3.7 venv`
    
 * activate virtual env:
    `source venv/bin/activate`
    
 * install all dependencies for the project:
   ```
    pip install -r requirements.txt
   ``` 
   in case if psycopg2 dependency fails to install just make sure to install it separately. 
   
 * create config file for execution:
   ```
        app-config:
          db-config:
             hostname: 127.0.0.1  ## postgres server address
             username: admin      ## postgres user-name  
             password: admin      ## postgres password
             default_db: test_db  
             port: 5432
          max-rows: 100           ## If the difference between two sqls has greater than 100 rows only the first 
                                  ## 100 rows are written to the output   
        
        table-config:
          test_table_1:                                ## name of the report
            src-relation: SELECT col1,col2,col3,col4 FROM source_table   ## source sql
            tgt-relation: SELECT col1,col2,col3,col4 FROM target_table   ## target sql 
            keys:                                      ## key fields in the above sql
                - col1
                - col2   

    ```
   In the above config file you define two SQLs the source sql and target sql. the source sql and target sql must have the
   same number of column with same labels. Then you should define the key fields which will be used to join these two
   relations.
   
#### sample execution

```
(venv) chlr@C02YJ30SJG5H Aiman (master) $ python -m data_diff.main -c config.conf -t test_table_1 -o output.html

            ====================================================================================================
            
            SELECT CASE WHEN t0.id IS NULL THEN t1.id ELSE t0.id END as id,CASE WHEN t0.name IS NULL THEN t1.name ELSE t0.name END as name,t0.address,t1.address,t0.killcount,t1.killcount 
            FROM 
            (SELECT * FROM test_table_1) t0 
            FULL OUTER JOIN 
            (SELECT * FROM test_table_2) t1 
            ON t0.id = t1.id AND t0.name = t1.name 
            WHERE (NOT (t0.address = t1.address AND t0.killcount = t1.killcount) OR  t0.id IS NULL  OR  t1.id IS NULL  OR  t0.name IS NULL  OR  t1.name IS NULL )
            
            ====================================================================================================
            
(venv) chlr@C02YJ30SJG5H Aiman (master) $ 

```
   
![Table data snapshot](https://github.com/rogue-one/aiman/blob/master/images/tables.png)

![Output file snapshot](https://github.com/rogue-one/aiman/blob/master/images/output.png)
   
   
      
