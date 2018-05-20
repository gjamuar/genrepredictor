import sys
import loggingmodule
import subprocess
import os
import codecs
from solr import SolrConnection
from solr.core import SolrException
import operator



#Define
currentPath = os.path.dirname(os.path.realpath(__file__))
DataPath = 'Data/'
#Spectrogram resolution
pixelPerSecond = 50
sliceSize = 128
#Tweakable parameters
desiredSize = 128

solrConnection = SolrConnection('http://aurora.cs.rutgers.edu:8181/solr/discogs_data_test')

def downloadYoutube(youtubeIds,foldername, genreName):
    print youtubeIds
    print foldername
    print genreName
    try:
        common_url = 'https://www.youtube.com/watch?v='
        outputPattern = foldername+'/'+genreName+'.%(autonumber)s.%(ext)s'
        args = ['youtube-dl', '--extract-audio', '--audio-format', 'wav','-o',outputPattern,'-i']
        for ids in youtubeIds:
            print ids
            print '****'
            args.append(common_url+ids)
        subprocess.call(args)

    except Exception as ex:
        logger_download.exception(ex)
#-------------------------------------------------------------------
#--------- Download songs from genres list ---------------------
def getYoutubeIdsfrom_genreList(genreList,nartist,nsongs):
    global solrConnection
    intersect = 0
    extravalues = []
    for genre in genreList:
        print genre
        genreQuery = 'genreMatch:"'+str(genre)+ '"'
        foldername = 'Data/'+genre
        print 'foldername: '+foldername
        createDirectory(foldername)
        retvalues = []
        try:
            response = solrConnection.query(q="*:*",fq=[genreQuery],version=2.2,wt = 'json',facet='true', facet_field='artistName',fl=['facet_fields'])
            intersect = int(response.results.numFound)
            if(intersect > 0):
                artist_dict = response.facet_counts['facet_fields']['artistName']
                print len(artist_dict)
                sorted_artist_dict = sorted(artist_dict.items(), key=operator.itemgetter(1),reverse = True)
                print sorted_artist_dict[0:nartist]
                for result in sorted_artist_dict[0:nartist]:
                    try:
                        curr_artist = result[0]
                        curr_query = 'artistName:"'+str(curr_artist) + '"'
                        response_ids = solrConnection.query(q="*:*",fq=[genreQuery,curr_query],version=2.2,wt = 'json',fl=['youtubeId','youtubeName'],rows = nsongs,sort='viewcountRate',sort_order='desc')
                        intersect1 = int(response_ids.results.numFound)
                        if(intersect1 >0):
                            for res in response_ids.results:
                                print str(res['youtubeId']) + '-----' + str(res['youtubeName'])+ '----'+str(res['viewcountRate'])
                                retvalues.append(str(res['youtubeId']))
                            downloadYoutube(retvalues,foldername, genre)
                    except Exception as ex:
                        logger_download.exception(ex)
        except Exception as ex:
            logger_download.exception(ex)
#---------------------------------------------------------------------
#Create empty Directory
def createDirectory(dirname):
    if(not os.path.exists(dirname)):
            os.mkdir(dirname,0755)

#------------- Main Program -----------------------------------------
if __name__ == '__main__':
    reload(sys)
    logger_download = loggingmodule.initialize_logger('downloadyoutube.log')
    sys.setdefaultencoding('utf8')
    createDirectory('Data')
    print '** Download songs by genres list **'
    filename = raw_input('Enter filename\n')
    nartist = input('Enter  the number of artists: \n')
    numofsongs = input('Enter number of songs per artist: \n')
    if os.path.exists(filename):
        fileopen = codecs.open(filename,"r","utf-8")
        lines = fileopen.readlines()
        lines = filter(lambda x: x.replace('\n','') != '',lines)
        lines = map(lambda x:x.replace('\n',''),lines)
    else:
        print 'File not found'

    getYoutubeIdsfrom_genreList(lines,nartist,numofsongs)
