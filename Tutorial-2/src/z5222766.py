from datetime import datetime

import flask
from flask import Flask, request
from flask_restplus import Api, Resource, fields, reqparse
from ordered_set import OrderedSet

import requests
import pandas as pd
import sqlite3

# with open('data.json') as f:
#   r = json.load(f)
# order_by = "+id, +creation_time"


app = Flask(__name__)
api = Api(app)

# user_indicator_id = api.model('Indicator', {
#     'indicator_id': fields.String
# })

parser_indicator = reqparse.RequestParser()
parser_indicator.add_argument('indicator_id', type=str, help='Indicator')

parser_order_by = reqparse.RequestParser()
parser_order_by.add_argument('order_by', type=str, help='order_by={+id,+creation_time,+indicator,-id,-creation_time,-indicator}')


@api.route('/collections/')
class DataImport(Resource):

    @api.expect(parser_indicator, validate=True)
    def post(self):
        ind_id = parser_indicator.parse_args()

        if not ind_id['indicator_id']:
            return {'message': 'Missing indicator_id, Please enter the id'}, 400

        response_data = requests.get(
            'http://api.worldbank.org/v2/countries/all/indicators/{0}?date=2012:2017&format=json&per_page=1000'.format(
                ind_id['indicator_id']))
        json_data = response_data.json()
        # with open('data.json') as f:
        #     r = json.load(f)

        if response_data.status_code != 200:
            return {'message': 'indicator_id {} is not available in the existing list of all countries'.format(
                ind_id['indicator_id'])}, 404

        dataset = pd.DataFrame(json_data[1])
        dataset['country'] = dataset['country'].apply(lambda x: x['value'])
        dataset['indicator_value'] = dataset['indicator'].apply(lambda x: x['value'])
        dataset['indicator'] = dataset['indicator'].apply(lambda x: x['id'])
        columns_to_drop = ['unit', 'obs_status', 'decimal', 'countryiso3code']
        dataset.drop(columns_to_drop, axis=1, inplace=True)
        dataset.dropna(inplace=True)
        dataset.reset_index(drop=True, inplace=True)

        conn = sqlite3.connect('z5222766.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

        # Initializations of the responses
        id = 0
        creation_time = str()

        if len(cursor.fetchall()) == 0:
            id = 1
            dataset['id'] = dataset.apply(lambda x: id, axis=1)
            creation_time = datetime.now()
            dataset['creation_time'] = dataset.apply(lambda x: creation_time, axis=1)
            dataset.to_sql('countries', conn, if_exists='append', index=False)
        else:
            sqlite_dataset = pd.read_sql('select * from countries', conn)
            indicator_list = list(sqlite_dataset['indicator'].unique())
            if ind_id['indicator_id'] not in indicator_list:
                list_id = list(sqlite_dataset['id'].unique())
                if len(list_id) == 0:
                    id = 1
                else:
                    id = max(list_id) + 1
                dataset['id'] = dataset.apply(lambda x: id, axis=1)
                creation_time = datetime.now()
                dataset['creation_time'] = dataset.apply(lambda x: creation_time, axis=1)
                dataset.to_sql('countries', conn, if_exists='append', index=False)
            else:
                indicator_match_subset = sqlite_dataset.loc[sqlite_dataset['indicator'] == ind_id['indicator_id']]
                data_extractor = indicator_match_subset.iloc[0]
                id = int(data_extractor['id'])
                creation_time = data_extractor['creation_time']

        cursor.close()
        return {
                   "uri": "/collections/{0}".format(id),
                   "id": str(id),
                   "creation_time": str(creation_time),
                   "indicator_id": ind_id['indicator_id']
               }, 201


@api.route('/collections/<string:id>')
class DataManipulation(Resource):

    # Task 4
    def get(self, id):
        connection = sqlite3.connect('z5222766.db')
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

        if len(cursor.fetchall()) == 0:
            return {"message": "Missing tables in the db"}, 400

        cursor.execute('SELECT id FROM countries;')
        if int(id) not in [item for ids in cursor.fetchall() for item in ids]:
            return {"message": "Collection ID {} doesn't exist".format(id)}, 404

        cursor.execute('SELECT * FROM countries WHERE id={};'.format(id))
        data = cursor.fetchall()

        entries = []
        for i in data:
            country_details = {'country': i[1], 'date': i[2], 'value': i[3]}
            entries.append(country_details)

        return {
                   "id": data[0][5],
                   "indicator": data[0][0],
                   "indicator_value": data[0][4],
                   "creation_time": data[0][6],
                   "entries": entries
               }, 200

    # Task 2
    def delete(self, id):
        connection = sqlite3.connect('z5222766.db')
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

        if len(cursor.fetchall()) == 0:
            return {"message": "Missing tables in the db"}, 400

        cursor.execute('SELECT * FROM countries;')
        if len(cursor.fetchall()) == 0:
            return {"message": "The table does not have any content, so deleting is not possible"}, 404

        cursor.execute('SELECT id FROM countries;')
        if int(id) not in [item for ids in cursor.fetchall() for item in ids]:
            return {"message": "Collection ID {} doesn't exist".format(id)}, 404

        cursor.execute('DELETE FROM countries WHERE id={};'.format(id))
        connection.commit()
        cursor.close()

        return {
                   "message": "The collection {} was removed from the database!".format(id),
                   "id": str(id)
               }, 200


@api.route('/collections/<string:id>/<string:year>/<string:country>')
class RetrieveEconomicIndicator(Resource):

    # Task 5
    def get(self, id, year, country):
        connection = sqlite3.connect('z5222766.db')
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

        if len(cursor.fetchall()) == 0:
            return {"message": "Missing tables in the db"}, 400

        cursor.execute('SELECT id FROM countries;')
        if int(id) not in [item for ids in cursor.fetchall() for item in ids]:
            return {"message": "Collection ID {} doesn't exist".format(id)}, 404

        cursor.execute('SELECT * FROM countries WHERE id=? AND date=? AND country=?;', (id, year, country))
        data = cursor.fetchall()
        print(data)

        if len(data) == 0:
            return {"message": "No record available in the database, please check the inputs again!"}, 404

        return {
                   "id": data[0][5],
                   "indicator": data[0][0],
                   "country": data[0][1],
                   "year": data[0][2],
                   "value": data[0][3]
               }, 200


parser_q = reqparse.RequestParser()
parser_q.add_argument('q', type=str, help='+N or -N')


@api.route('/collections/<string:id>/<string:year>/')
class RetrieveEconomicIndicator(Resource):

    # Task 6
    @api.expect(parser_q, validate=True)
    def get(self, id, year):
        connection = sqlite3.connect('z5222766.db')
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

        if len(cursor.fetchall()) == 0:
            return {"message": "Missing tables in the db"}, 400

        cursor.execute('SELECT id FROM countries;')
        if int(id) not in [item for ids in cursor.fetchall() for item in ids]:
            return {"message": "Collection ID {} doesn't exist".format(id)}, 404

        q = parser_q.parse_args()

        if q['q'][0] != '+' and q['q'][0] != '-':
            return {"message": "Query {} not available".format(q['q'])}, 400

        N = int(q['q'][1:])
        if q['q'].startswith('+'):
            cursor.execute('SELECT * FROM countries WHERE id=? AND date=? ORDER BY value DESC;', (id, year))
        elif q['q'].startswith('-'):
            cursor.execute('SELECT * FROM countries WHERE id=? AND date=? ORDER BY value ASC;', (id, year))
        data = cursor.fetchall()

        if len(data) == 0:
            return {"message": "The query {} cannot be searched because of insufficient data".format(q['q'])}, 404

        entries = []
        for i in range(0, N):
            country_details = {'country': data[i][1], 'value': data[i][3]}
            entries.append(country_details)

        return {
                   "indicator": data[0][0],
                   "indicator_value": data[0][4],
                   "entries": entries
               }, 200


if __name__ == '__main__':
    app.run(debug=True)
