from flask import Flask, request, render_template
from flask_restful import Resource, Api
from pymongo import MongoClient
from flask_restful import fields, marshal_with, reqparse, inputs
import random
from bson.son import SON

from credentials import MONGOLAB_URL

rootdir = '../images/faces'
image_url = 'http://facedepot.s3.amazonaws.com/{image}.jpg'
article_url = 'http://nla.gov.au/nla.news-article{article_id}'

app = Flask(__name__)
api = Api(app)

face_fields = {
    'image_url': fields.FormattedString(image_url),
    'article_url': fields.FormattedString(article_url),
    'date': fields.DateTime(dt_format='iso8601'),
    'width': fields.Integer,
    'height': fields.Integer,
    'title': fields.String,
    'title_id': fields.String
}


def get_fd_faces():
    dbclient = MongoClient(MONGOLAB_URL)
    db = dbclient.get_default_database()
    collection = db.fd_faces
    return collection


class GetFaces(Resource):
    @marshal_with(face_fields)
    def get(self):
        number = int(request.args.get('n', 20))
        parser = reqparse.RequestParser()
        parser.add_argument('n', type=int, default=20)
        parser.add_argument('year', type=int)
        parser.add_argument('title_id', type=str)
        args = parser.parse_args()
        if args['n'] > 100:
            number = 100
        else:
            number = args['n']
        collection = get_fd_faces()
        query = {'random_id': {'$near': [random.random(), 0]}}
        if args['year']:
            query['year'] = int(args['year'])
        if args['title_id']:
            query['title_id'] = args['title_id']
        faces = list(collection.find(query).limit(number))
        return faces


class GetTitles(Resource):
    def get(self):
        pipeline = [
            {"$group": {"_id": {"title_id": "$title_id", "title": "$title"}, "faces": {"$sum": 1}}},
            {"$project": {"_id": 0, "title_id": "$_id.title_id", "title": "$_id.title", "faces": "$faces"}},
            {"$sort": SON([("title", 1)])},
        ]
        collection = get_fd_faces()
        titles = list(collection.aggregate(pipeline))
        return titles


class GetYears(Resource):
    def get(self):
        pipeline = [
            {"$group": {"_id": "$year", "faces": {"$sum": 1}}},
            {"$project": {"_id": 0, "year": "$_id", "faces": "$faces"}},
            {"$sort": SON([("year", 1)])}
        ]
        collection = get_fd_faces()
        years = list(collection.aggregate(pipeline))
        return years


@app.route('/')
def home():
    return render_template('home.html')


api.add_resource(GetFaces, '/faces')
api.add_resource(GetTitles, '/titles')
api.add_resource(GetYears, '/years')

if __name__ == '__main__':
    app.run(debug=True)
