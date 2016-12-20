#!/usr/bin/env python

import os, sys, getopt
import urllib, requests
import sqlite3
import base64, json

import pandas as pd

from addons import *

global conf_file, db_file
conf_file = 'edmunds.conf'
db_file = 'edmunds.db'


def main(argv):
    vin = None
    mileage = None
    csv = None

    condition = 'clean'
    zip = 10004
    api_key = b64()['api_key']

    # Parse command line arguments
    try:
        opts, args = getopt.getopt(argv, "hv:m:c:", ['help', 'vin=', 'mileage=', 'csv='])
    except getopt.GetoptError:
        usage(sys.argv[0])
        sys.exit(2)

    # The user running the script can either supply vin & mileage or a csv filename but not both
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(sys.argv[0])
            sys.exit()

        # Only --csv or -c is allowed
        if len(argv) < 2:
            if opt in ('-c', '--csv'):
                csv = arg
            else:
                usage(sys.argv[0])
                sys.exit()
        # At most 2 arguments are allowed
        elif len(argv) > 2:
                usage(sys.argv[0])
                sys.exit()

        # Only both --vin or -v and --mileage or -m are allowed
        elif len(argv) == 2:
            if opt in ('-v', '--vin'):
                vin = arg.lower()
            elif opt in ('-m', '--mileage'):
                mileage = arg
            else:
                usage(sys.argv[0])
                sys.exit()

    if not csv is None:
        try:
            with open(csv) as data:
                for i, line in enumerate(data.readlines()):
                    if i > 0:
                        vin, make, model, year, trim, style, odometer = [e.lower().strip() for e in line.replace('\n', '').split(',')]
                        # Find VIN locally
                        if sql_get_vin(vin) is None:
                            car = edmunds_get_style(vin, api_key)
                            # VIN was not found locally, thus, pull the price via Edmund's
                            if not car is None:
                                tmv = edmunds_get_tmv(car['style'], condition, odometer, api_key)
                                if not sql_add_car(car, tmv) is None:
                                    print(single_car(car, tmv, source='edmunds'))
                            # VIN doesn't exist anywhere
                            else:
                                print('vin:\t{}\n\t\twas not found\n\n\n'.format(vin))
                        # VIN was found locally, thus, pull the price from the DB
                        else:
                            print(single_car(sql_get_car(vin)))

        except FileNotFoundError as err:
            print(err)
        except FileExistsError as err:
            print(err)
        return 0
    else:
        # Find VIN locally
        if sql_get_vin(vin) is None:
            car = edmunds_get_style(vin, api_key)
            # VIN was not found locally, thus, pull the price via Edmund's
            if not car is None:
                tmv = edmunds_get_tmv(car['style'], condition, mileage, api_key)
                if not sql_add_car(car, tmv) is None:
                    print(single_car(car, tmv, source='edmunds'))
            # VIN doesn't exist anywhere
            else:
                print('vin:\t{}\n\t\twas not found\n\n\n'.format(vin))
                # VIN was found locally, thus, pull the price from the DB
        else:
            print(single_car(sql_get_car(vin)))


if __name__ == "__main__":
    # Initialize database if doesn't exist
    if not os.path.exists(db_file):
        init_db()

    if len(sys.argv[1:]) > 0:
        main(sys.argv[1:])
    else:
        usage(sys.argv[0])



