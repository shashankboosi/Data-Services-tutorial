from datetime import datetime

import flask
from flask import Flask, request
from flask_restplus import Api, Resource, fields, reqparse

import requests
import pandas as pd
import json
import sqlite3

# with open('data.json') as f:
#     r = json.load(f)


app = Flask(__name__)
api = Api(app)

user_indicator_id = api.model('Indicator', {
    'indicator_id': fields.String
})


@api.route('/collections/')
class DataImport(Resource):

    @api.expect(user_indicator_id, validate=True)
    def post(self):
        ind_id = flask.request.json

        if not ind_id['indicator_id']:
            return {'message': 'Missing indicator_id, Please enter the id'}, 400

        response_data = requests.get(
            'http://api.worldbank.org/v2/countries/all/indicators/{0}?date=2012:2017&format=json&per_page=1000'.format(
                ind_id))
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
        print(dataset.head())

        conn = sqlite3.connect('z5222766.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

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
            print(indicator_list)
            if ind_id['indicator_id'] not in indicator_list:
                print('x')
                max_id = max(list(sqlite_dataset['id'].unique()))
                id = max_id + 1
                dataset['id'] = dataset.apply(lambda x: id, axis=1)
                creation_time = datetime.now()
                dataset['creation_time'] = dataset.apply(lambda x: creation_time, axis=1)
                dataset.to_sql('countries', conn, if_exists='append', index=False)
            else:
                print('xxc')
                indicator_match_subset = sqlite_dataset.loc[sqlite_dataset['indicator'] == ind_id['indicator_id']]
                print(indicator_match_subset)
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

    # def put(self, todo_id):
    #     todos[todo_id] = request.form['data']
    #     return {todo_id: todos[todo_id]}


if __name__ == '__main__':
    app.run(debug=True)
