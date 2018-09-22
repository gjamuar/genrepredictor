from subprocess import Popen, PIPE, STDOUT
import os
# import sox
# import shutil
from PIL import Image

#Define
currentPath = os.path.dirname(os.path.realpath(__file__))
DataPath = 'Data/'
#Spectrogram resolution
pixelPerSecond = 64
sliceSize = 128
#Tweakable parameters
desiredSize = 128

#-------------------------------------------------------------------
#Create empty Directory
def createDirectory(dirname):
    if(not os.path.exists(dirname)):
            os.mkdir(dirname,0755)
#-----------------------------------------------
#---------------------------------------------------------------------
def createSpctogram(filepath, output_train, output_test, wav_train, wav_test):
    try:
        # #songs files to mono, trim, 24Hz for Training
        print 'wav for training: '+ filepath
        command = "sox '{}' -r 24000 '{}' remix 1 trim 25 00:00:60.00".format(filepath, wav_train)
        p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True, cwd=currentPath)
        output, errors = p.communicate()
        if errors:
           print errors

        #songs files to mono, trim, 24Hz for Testing
        print 'wav for testing: '+ filepath
        command = "sox '{}' -r 24000 '{}' remix 1 trim 85 00:00:60.00".format(filepath, wav_test)
        p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True, cwd=currentPath)
        output, errors = p.communicate()
        if errors:
           print errors

        print 'Spectogram for Training and Testing for: '+ filepath
        #Songs to mono, trim and spctograms for Training
        command = "sox '{}' -r 24000 -n remix 1 trim 25 00:00:60.00 spectrogram -Y 200 -X {} -m -r -o '{}.png'".format(filepath,pixelPerSecond,output_train)
        
        p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True, cwd=currentPath)
        output, errors = p.communicate()
        if errors:
           print errors

        #Songs to mono, trim and spctograms for Testing
        command = "sox '{}' -r 24000 -n remix 1 trim 85 00:00:60.00 spectrogram -Y 200 -X {} -m -r -o '{}.png'".format(filepath,pixelPerSecond,output_test)
        
        p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True, cwd=currentPath)
        output, errors = p.communicate()
        if errors:
           print errors
    except Exception as ex:
        print ex

#---------------------------------------------------------------------
def createSlices(filename, dirname,output_train, output_test):
    #-- Create Slices for Training ---
    try:
        genre = dirname
        slicepath_train = 'slices_train/'+genre+'/'
        img = Image.open(output_train+'.png')
        width, height = img.size
        nbSamples = int(width/desiredSize)
        width - desiredSize

        print "Creating slice for Training: for", output_train+'.png'
        for i in range(nbSamples):
            #print "Creating slice for Training: ", (i+1), "/", nbSamples, "for", output_train+'.png'
            startPixel = i * 128
            imgTmp = img.crop((startPixel, 1, startPixel + desiredSize, desiredSize + 1))
            imgTmp.save(slicepath_train+"{}_{}.png".format(filename+'.png'[:-4],i))

        #-- Create Slices for Testing ---
        slicepath_test = 'slices_test/'+genre+'/'
        img = Image.open(output_test+'.png')
        width, height = img.size
        nbSamples = int(width/desiredSize)
        width - desiredSize

        print "Creating slice for Test: for", output_test+'.png'
        for i in range(nbSamples):
            #print "Creating slice for Testing: ", (i+1), "/", nbSamples, "for", output_test+'.png'
            startPixel = i * 128
            imgTmp = img.crop((startPixel, 1, startPixel + desiredSize, desiredSize + 1))
            imgTmp.save(slicepath_test+"{}_{}.png".format(filename+'.png'[:-4],i))
           
    except Exception as ex:
        print ex


# ---------------------------------------------------------------------
def createSlicesForSong(datapath, youtubeId):
    # -- Create Slices for Training ---
    try:
        genre = youtubeId
        slicepath_train = datapath + genre + '/'
        img = Image.open(slicepath_train + youtubeId + '.png')
        width, height = img.size
        nbSamples = int(width / desiredSize)
        width - desiredSize

        print "Creating slice for Training: for", youtubeId + '.png'
        for i in range(nbSamples):
            # print "Creating slice for Training: ", (i+1), "/", nbSamples, "for", output_train+'.png'
            startPixel = i * 128
            imgTmp = img.crop((startPixel, 1, startPixel + desiredSize, desiredSize + 1))
            imgTmp.save(slicepath_train + "{}#{}#part.png".format(youtubeId + '.png'[:-4], i))

    except Exception as ex:
        print ex


#---------------------------------------------------------
#Convert songs to Mono, Trimmed and spectograms.
#def createMonoTrim_spcto_slice(filename, dirname, balancingFile):

def createMonoTrim_spcto_slice(filename, dirname):
    createDirectory('specto_train')
    createDirectory('specto_test')
    createDirectory('wav_train')
    createDirectory('wav_test')
    createDirectory('wav_train/'+dirname)
    createDirectory('wav_test/'+dirname)
    createDirectory('specto_train/'+dirname)
    createDirectory('specto_test/'+dirname)
    filepath = DataPath+dirname+'/'+filename
    wav_train = 'wav_train/'+dirname+'/'+filename
    wav_test = 'wav_test/'+dirname+'/'+filename
    output_train = 'specto_train/'+dirname+'/'+filename
    output_test = 'specto_test/'+dirname+'/'+filename
    createDirectory('slices_train/')
    createDirectory('slices_test/')
    createDirectory('slices_train/'+dirname)
    createDirectory('slices_test/'+dirname)

    createSpctogram(filepath, output_train, output_test, wav_train, wav_test)
    createSlices(filename, dirname,output_train, output_test)

#------------- Main Program -----------------------------------------
if __name__ == '__main__':
    dirs = os.listdir(DataPath)
    for dirname in dirs:
        if dirname=='.DS_Store':
            continue
        files = os.listdir(DataPath+dirname)
        for filename in files:
            #print filename
            if filename!='.DS_Store':
                createMonoTrim_spcto_slice(filename, dirname)
