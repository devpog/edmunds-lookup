def sql_get_vin(vin, db='edmunds.db'):
    import sqlite3

    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()

        sql = "select * from vehicle where vin = '{}'".format(vin)
        cur.execute(sql)
        rows = cur.fetchall()
        conn.close()

        if len(rows) > 0:
            return rows
        else:
            return None
    except Exception as err:
        print(err)
        return 1


def sql_add_make(name, db='edmunds.db'):
    import sqlite3

    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()

        sql = "insert into make (name) values ('{}')".format(name.lower())
        cur.execute(sql)
        conn.commit()

        id = cur.execute("select max(make) from make").fetchall().pop()[0]
        conn.close()

        return id
    except Exception as err:
        print(err)
        return 1


def sql_get_make(name=None, db='edmunds.db'):
    import sqlite3

    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()

        if name is None:
            sql = "select * from make"
        else:
            sql = "select * from make where name = '{}'".format(name.lower())

        cur.execute(sql)
        rows = cur.fetchall()
        conn.close()

        if len(rows) > 0:
            if name is None:
                return rows
            else:
                return rows[0][0]
        else:
            return None
    except Exception as err:
        print(err)
        return 1


def sql_add_model(name, make, db = 'edmunds.db'):
    import sqlite3

    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()

        sql = "insert into model (make, name) values ({}, '{}')".format(make, name.lower())
        cur.execute(sql)
        conn.commit()

        id = cur.execute("select max(model) from model where make = {}".format(make)).fetchall().pop()[0]
        conn.close()

        return id
    except Exception as err:
        print(err)
        return 1


def sql_get_model(name=None, make=None, db='edmunds.db'):
    import sqlite3

    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()

        if name is None:
            if make is None:
                sql = "select * from model"
            else:
                sql = "select * from model where make = {}".format(make)
        else:
            if make is None:
                sql = "select * from model where name = '{}'".format(name.lower())
            else:
                sql = "select * from model where name = '{}' and make = {}".format(name.lower(), make)

        cur.execute(sql)
        rows = cur.fetchall()
        conn.close()

        if len(rows) > 0:
            if name is None:
                return rows
            else:
                return rows[0][0]
        else:
            return None
    except Exception as err:
        print(err)
        return 1


def sql_add_body(name, db = 'edmunds.db'):
    import sqlite3

    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()

        sql = "insert into body (name) values ('{}')".format(name.lower())

        cur.execute(sql)
        conn.commit()

        id = cur.execute("select max(body) from body").fetchall().pop()[0]
        conn.close()

        return id
    except Exception as err:
        print(err)
        return 1


def sql_get_body(name=None, db = 'edmunds.db'):
    import sqlite3

    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()

        if name is None:
            sql = "select * from body"
        else:
            sql = "select * from body where name = '{}'".format(name.lower())

        rows = cur.execute(sql).fetchall()
        conn.close()

        if len(rows) > 0:
            if name is None:
                return rows
            else:
                return rows[0][0]
        else:
            return None
    except Exception as err:
        print(err)
        return 1


def sql_get_car(vin=None, db = 'edmunds.db'):
    import sqlite3
    headers = ['vin', 'make', 'model', 'year', 'body', 'price_certified', 'price_private', 'price_retail', 'price_trade']

    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()

        if not vin is None:
            sql = """
            select
            vehicle.vin, make.name, model.name, vehicle.year, body.name,
            vehicle.price_certified, vehicle.price_private, vehicle.price_retail, vehicle.price_trade
            from vehicle
            inner join make on vehicle.make = make.make
            inner join model on vehicle.model = model.model
            inner join body on vehicle.body = body.body
            where vin = '{}'
            """.format(vin.lower())
        else:
            sql = "select * from vehicle"
        rows = cur.execute(sql).fetchall()
        conn.close()

        if len(rows) > 0:
            if vin is None:
                return rows
            else:
                car = dict()
                row = rows[0]
                for i, h in enumerate(headers):
                    car[h] = str(row[i])
                return car
        else:
            return None
    except Exception as err:
        print(err)
        return 1


def sql_add_car(car, tmv, db = 'edmunds.db'):
    '''
    :param car = dictionary:
    :param tmv = dictionary:
    :param db = default:
    :return = 0 || None:
    '''
    import sqlite3
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        row = []
        # Look up make's id in the DB, if not found create a new one
        make_id = sql_get_make(car['make'])
        if make_id is None:
            make_id = sql_add_make(car['make'])

        # Look up model's id in the DB, if not found create a new one
        model_id = sql_get_model(make=make_id, name=car['model'])
        if model_id is None:
            model_id = sql_add_model(car['model'], make_id)

        # Look up body's id in the DB, if not found create a new one
        body_id = sql_get_body(car['body'])
        if body_id is None:
            body_id = sql_add_body(car['body'])

        vin = car['vin']
        year = car['year']
        price_certified = tmv['price_certified']
        price_private = tmv['price_private']
        price_retail = tmv['price_retail']
        price_trade = tmv['price_trade']

        sql = """
        insert into vehicle (vin, make, model, year, body, price_certified, price_private, price_retail, price_trade)
            values ('{}', {}, {}, {}, {}, {}, {}, {}, {})
        """.format(vin, make_id, model_id, year, body_id, price_certified, price_private, price_retail, price_trade)

        cur.execute(sql)
        conn.commit()
        conn.close()

        return 0
    except Exception as err:
        print(err)
        return None


def edmunds_get_style(vin, api_key):
    import requests

    api_call = "https://api.edmunds.com/api/vehicle/v2/vins/{}?fmt=json&api_key={}".format(vin, api_key)

    row = dict()
    response = requests.get(api_call)
    if response.status_code == 200:
        r = response.json()

        make = r['make']['name']
        years = r['years'][0]
        year = years['year']

        styles = years['styles'][0]
        style_id = styles['id']
        body = styles['submodel']['body']
        model = styles['submodel']['modelName']

        row['vin'] = vin.lower()
        row['model'] = model.lower()
        row['year'] = year
        row['body'] = body.lower()
        row['make'] = make.lower()
        row['style'] = style_id

        return row
    else:
        return None

def edmunds_get_tmv(style, condition, mileage, api_key, zip='10004'):
    import requests

    api_call = "https://api.edmunds.com/v1/api/tmv/tmvservice/calculateusedtmv?styleid={}&condition={}&mileage={}&zip={}&fmt=json&api_key={}".format(style, condition, mileage, zip, api_key)

    row = dict()
    try:
        response = requests.get(api_call)
        if response.status_code == 200:
            r = response.json()['tmv']
            tvm = r['totalWithOptions']

            price_certified = r['certifiedUsedPrice']
            price_private = tvm['usedPrivateParty']
            price_retail = tvm['usedTmvRetail']
            price_trade = tvm['usedTradeIn']

            row['style'] = style
            row['price_certified'] = price_certified
            row['price_private'] = price_private
            row['price_retail'] = price_retail
            row['price_trade'] = price_trade

            return row
        else:
            return None
    except Exception as err:
        print(err)


def init_db(f='init.sql', db_file='edmunds.db'):
    import sqlite3

    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    try:
        with open(f) as data:
            sql = data.read()
            cur.executescript(sql)
            cur.close()
            conn.close()

            return 0
    except FileNotFoundError as err:
        print(err)
    except FileExistsError as err:
        print(err)


def b64(f='edmunds.conf', encoded=False):
    import base64
    params = dict()

    try:
        with open(f) as data:
            for line in data.readlines():
                if not line.startswith('#'):
                    k = line.split('=')[0].replace('\n', '').strip()
                    if encoded:
                        v = base64.b64decode(line.split('=')[1].replace('\n', '').strip() + '=').decode('utf-8')
                    else:
                        v = line.split('=')[1].replace('\n', '').strip()
                    params[k] = v
    except FileNotFoundError as err:
        print(err)
        return 2
    except FileExistsError as err:
        print(err)
        return 2
    return params


def single_car(car, tvm=None, source='local'):
    if not tvm is None:
        for k, v in tvm.items():
            car[k] = v

    row = """
          vin:\t{}
          source:\t{}
          make:\t{}
          model:\t{}
          year:\t{}
          body:\t{}
          price_certified:\t{}
          price_private:\t{}
          price_retail:\t{}
          price_trade:\t{}
          """.format(car['vin'], source, car['make'], car['model'], car['year'], car['body'],
                     car['price_certified'], car['price_private'], car['price_retail'], car['price_trade'])
    return row.strip() + '\n\n\n'


def usage(name=None):
    help = """
    Usage:

    This script find the price of a used vehicle via Edmund's portal.
    There are two ways of using it. Either a csv file's name is provided or
    vin number along with odometer's readings. See below:

    {name} --vin=[vin] --mileage=[mileage]
    {name} -v[vin] -m[mileage]

    OR

    {name} --csv=[file_name]
    {name} -c[file_name]

    Created by Kip Pogrebenko
    """.format(name=name)
    print(help)
