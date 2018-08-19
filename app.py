from flask import Flask, jsonify, abort, make_response, request
from genres_predictor import GenrePredictor
import json
#import db_utility
import loggingmodule
import argparse
import os
import glob

app = Flask(__name__)
params = {}
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

#genres_predictor = GenrePredictor('models_for_prediction/1st_level/', '9353', 4)
#style_predictor = GenrePredictor('models_for_prediction/2nd_level/blues/', '8231', 13)
@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})
def get_genresCount():
    filename = os.path.join(params['path'],'genres.txt')
    if(os.path.exists(filename)):
        fo = open(filename, "rw+")
        genreCount = len(fo.readlines())
    else:
        genreCount = -1
    print 'Returning :'+str(genreCount)
    return genreCount

def get_predictorname():
    list_meta_files = [os.path.join(params['path'], f) for f in os.listdir(params['path']) if f.endswith(".meta")]
    #files = os.system('find '+params['path']+' -name "[0-9]*.meta" ')
    predict_name = ''
    if(len(list_meta_files) > 0):
        predict_name = os.path.splitext(os.path.basename(list_meta_files[0]))[0]
    else:
        print 'cant find meta file'
    print predict_name
    return predict_name
    

@app.route('/gramusik/v1/predict/<string:youtube_id>', methods=['GET'])
def find_genres(youtube_id):
    global genres_predictor
    is_force_download = False
    if 'refresh' in request.args:
        is_force_download = request.args['refresh']
    if is_force_download == 'True' or is_force_download == 'true':
        genres_predictor.deleteProcessedMarker(youtube_id)
    genres_predictor.download_youtube(youtube_id)
    predicted_list, prediction_nolable, genreslabel, combinedprediction, combinedprediction_withlable, inc_prediction = genres_predictor.predict(youtube_id)
    genres_predictor.deleteWavAndMarkProcessed(youtube_id)
    # convert to json data
    # predictionstr = json.dumps(prediction)
    # return jsonify({'youtube_id': youtube_id, 'predictedlist': predictedlist})
    #return json.dumps(predictedlist)
    jsonresp = json.dumps({
        'youtube_id': youtube_id, 'prediction': predicted_list, 'prediction_nolable': prediction_nolable,
        'label': genreslabel, 'combinedprediction': combinedprediction,
        'combinedprediction_withlable': combinedprediction_withlable, 'incremental_prediction': inc_prediction})
    # print("Response is:")
    # print(jsonresp)
    # db_utility.execute(
    #     "INSERT IGNORE INTO genrepredictor.Level1Prediction (`YoutubeId`, `GenreCode`, `Prediction`)"
    #     " VALUES (%s, %s, %s )",
    #     (youtube_id, ':'.join(genreslabel), jsonresp))
    respobj = json.loads(jsonresp)
    return jsonify(respobj)
    # resp = jsonify({
    #     'youtube_id': youtube_id, 'prediction': predicted_list, 'prediction_nolable': prediction_nolable,
    #     'label': genreslabel,'combinedprediction': combinedprediction,
    #     'combinedprediction_withlable':combinedprediction_withlable, 'incremental_prediction': inc_prediction})



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
    global genres_predictor
    logger_predict = loggingmodule.initialize_logger('predictor','genre_predictor.log')
    parser = argparse.ArgumentParser()
    parser.add_argument('-path',"--path", help="path to the data model")

    #parser = argparse.ArgumentParser()
    parser.add_argument('-port',"--port", help="port number of the application")

    #parser = argparse.ArgumentParser()
    #parser.add_argument('-n',"--name", help="name of the predictor")
    
    #parser = argparse.ArgumentParser()
    #parser.add_argument('-g',"--genrescount", help="number of genres")

    args = parser.parse_args()
    if('path' in args and args.path != ''):
        params['path'] = args.path
    else:
        params['path'] = 'models_for_prediction/1st_level/'
    if('port' in args and args.port != ''):
        params['port'] = int(args.port)
    else:
        params['port'] = 8970
    #params['name'] = args.name
    #params['genrescount'] = int(args.genrescount)
    

    genreCount = get_genresCount()
    if(genreCount == -1):
        print 'genres.txt not found'
    predict_name = get_predictorname();
    genres_predictor = GenrePredictor(params['path'], predict_name, genreCount)

    app.run(host='0.0.0.0', port=params['port'])
