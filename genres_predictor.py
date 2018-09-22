import sys
import loggingmodule
import subprocess
import os.path
from model import createModel
from imageFilesTools import createDatasetFromSlicesPredict
import numpy
from shutil import rmtree
import tensorflow as tf
from wav_specto_slice_for_ExistingFiles import createSlicesForSong


# import codecs
# from solr import SolrConnection
# from solr.core import SolrException
# import operator

# Define
currentPath = os.path.dirname(os.path.realpath(__file__))
DataPath = 'DownloadedData/'
# Spectrogram resolution
pixelPerSecond = 50
sliceSize = 128
# Tweakable parameters
desiredSize = 128

logger_download = loggingmodule.initialize_logger('downloadyoutube.log')


# solrConnection = SolrConnection('http://aurora.cs.rutgers.edu:8181/solr/discogs_data_test')

def inc_avg(li):
    """Calculate the average incrementally.
    Input: a list.
    Output: average of the list."""
    left = 0
    right = len(li) - 1

    avg = li[left]
    left += 1
    result = []

    while left <= right:
        curr = left + 1
        avg += (li[left] - avg) / float(curr)
        result.append(avg)
        left += 1

    return result


class GenrePredictor(object):

    def __init__(self, path, model_name, num_of_genres):
        self.G1 = tf.Graph()
        self.G2 = tf.Graph()
        with self.G1.as_default():
            self.model = createModel(num_of_genres, sliceSize)
            print("[+] Loading weights in first graph...")
            self.model.load(path + model_name, weights_only=True)
            self.level1genres = GenrePredictor.readGenresFile(path)

        with self.G2.as_default():
            self.bluemodel = createModel(13, sliceSize)

#           self.model.load('models_for_prediction/1st_level/musicDNN.tflearn')
#             self.bluemodel.load('models_for_prediction/2nd_level/blues/8231',weights_only=True)
        #self.level2genres = GenrePredictor.readGenresFile('models_for_prediction/2nd_level/blues/')
        print(self.level1genres)
        print("    Weights loaded!")

    @staticmethod
    def download_youtube(youtubeId):

        if os.path.exists(DataPath + youtubeId + '/' + youtubeId + '.processed'):
            print(youtubeId + "already downloaded and processed, skipping downloading")
            return

        try:
            # args = ['youtube-dl', '--extract-audio', '--quite', '--audio-format', 'wav', '-o', outputPattern, '-i',
            #         common_url + youtubeId, '&&', 'sox', youtubeId + '.wav', '-r', '24000', '-n', 'remix', '1', 'trim',
            #         '25', '00:00:60.00',
            #         'spectrogram', '-Y', '200',
            #         ]
            if not os.path.exists(DataPath + youtubeId + '/' + youtubeId + '.wav'):
                common_url = 'https://www.youtube.com/watch?v='
                outputpattern = DataPath + youtubeId + '/' + '%(id)s.%(ext)s'
                args = ['youtube-dl', '--extract-audio', '--quiet', '--audio-format', 'wav', '-o', outputpattern, '-i',
                        common_url + youtubeId]
                subprocess.call(args)
            # args = ['sox', DataPath + youtubeId + '/' + youtubeId + '.wav', '-r', '24000', '-n', 'remix', '1', 'trim', '25',
            #         '00:00:60.00', 'spectrogram', '-Y', '200', '-X', '64', '-m', '-r', '-o',
            #         DataPath + youtubeId + '/' + youtubeId + '.png']
            if not os.path.exists(DataPath + youtubeId + '/' + youtubeId + '.png'):
                args = ['sox', DataPath + youtubeId + '/' + youtubeId + '.wav', '-r', '24000', '-n', 'remix', '1',
                        'spectrogram', '-Y', '200', '-X', '64', '-m', '-r', '-o',
                        DataPath + youtubeId + '/' + youtubeId + '.png']
                subprocess.call(args)
                createSlicesForSong(DataPath, youtubeId)
                # args = ['convert', '-crop', '128x129', DataPath + youtubeId + '/' + youtubeId + '.png',
                #         DataPath + youtubeId + '/' + youtubeId + '#%d#part.png']
                # subprocess.call(args)
        except Exception as ex:
            logger_download.exception(ex)

    def predict(self, youtube_id):
        test_X, test_y = createDatasetFromSlicesPredict(sliceSize, DataPath + youtube_id)
        #print(test_X)
        # model = createModel(3, sliceSize)
        # print("[+] Loading weights...")
        # model.load('models_for_prediction/TOP/musicDNN.tflearn')
        # print("    Weights loaded!")
        # with self.G2.as_default():
        predicted_label1 = self.model.predict_label(test_X)
        prediction = self.model.predict(test_X)
        #print(prediction)
        preditionlist = [dict(zip(self.level1genres, ([numpy.float64(x) * 100 for x in sliceprediction]))) for sliceprediction in prediction]
        print(preditionlist)
        prediction_nolable = [[numpy.float64(x) * 100 for x in sliceprediction] for sliceprediction in prediction]
        #print(predicted_label1)
        #print(prediction_nolable)
        combinedprediction = numpy.mean(prediction_nolable, axis=0)
        combinedprediction = [numpy.float64(x) for x in combinedprediction]
        combinedprediction_withlable = sorted(zip(self.level1genres, [numpy.float64(x) for x in combinedprediction]),
                                              key=lambda y: y[1], reverse=True)
        #print(combinedprediction)

        unziped_prediction = zip(*prediction_nolable)
        unziped_inc_avg_prediction = [inc_avg(li) for li in unziped_prediction]
        #inc_prediction = zip(ls for ls in unziped_inc_avg_prediction)
        inc_prediction = zip(*unziped_inc_avg_prediction)

        print(inc_prediction)

        return preditionlist, prediction_nolable, self.level1genres, combinedprediction, combinedprediction_withlable, inc_prediction

        # for y in test_X:
        #     print("Predicting genres...")
        #     print y
        #     print("Predict_data shape" + str(y.shape))
        #     predicted_label = model.predict_label(y)
        #     print("====================================")
        #     print("Predicting labels:")
        #     print(predicted_label)
        #     print("====================================")
        # return

    @staticmethod
    def deleteWavAndMarkProcessed(youtubeId):
        if os.path.exists(DataPath + youtubeId + '/' + youtubeId + '.wav'):
            os.remove(DataPath + youtubeId + '/' + youtubeId + '.wav')
            open(DataPath + youtubeId + '/' + youtubeId + '.processed', 'w').close()

    @staticmethod
    def readGenresFile(path):
        with open(path + 'genres.txt', 'r') as f:
            genreslist = f.read().strip().splitlines()
            return genreslist

    @staticmethod
    def deleteProcessedMarker(youtube_id):
        if os.path.exists(DataPath + youtube_id + '/' + youtube_id + '.processed'):
            rmtree(DataPath + youtube_id)

if __name__ == '__main__':
    genre_predictor = GenrePredictor('models_for_prediction/1st_level/', '9353', 4)
    GenrePredictor.download_youtube('WxTofWwtmNE')
    genre_predictor.predict('WxTofWwtmNE')
