from flask import Flask, jsonify, abort, make_response, request
from genres_predictor import GenrePredictor
import json

app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]

genres_predictor = GenrePredictor('models_for_prediction/1st_level/', '9353', 4)
#style_predictor = GenrePredictor('models_for_prediction/2nd_level/blues/', '8231', 13)

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})


@app.route('/gramusik/v1/predict/<string:youtube_id>', methods=['GET'])
def find_genres(youtube_id):
    args = request.args
    is_force_download = args['refresh']
    if is_force_download == 'True' or is_force_download == 'true':
        genres_predictor.deleteProcessedMarker(youtube_id)
    genres_predictor.download_youtube(youtube_id)
    predicted_list, prediction_nolable, genreslabel, combinedprediction, combinedprediction_withlable, inc_prediction = genres_predictor.predict(youtube_id)
    genres_predictor.deleteWavAndMarkProcessed(youtube_id)
    # convert to json data
    # predictionstr = json.dumps(prediction)
    # return jsonify({'youtube_id': youtube_id, 'predictedlist': predictedlist})
    #return json.dumps(predictedlist)
    return jsonify({
        'youtube_id': youtube_id, 'prediction': predicted_list, 'prediction_nolable': prediction_nolable,
        'label': genreslabel,'combinedprediction': combinedprediction,
        'combinedprediction_withlable':combinedprediction_withlable, 'incremental_prediction': inc_prediction})


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})


@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8978)
