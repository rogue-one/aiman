"""
Usage:
   data_diff [ -h | --help ]
   data_diff ( -c INPUT_CONFIG_FILE ) ( -t INPUT_TABLE ) ( -o OUTPUT_FILE )

-h --help    help message
-c           Input config file
-t           src table to compare
-o           output file

"""

from docopt import docopt
from app import App

if __name__ == '__main__':
    args = docopt(__doc__)
    App(args).run()
