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