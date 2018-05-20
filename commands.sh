youtube-dl --extract-audio --quiet  --audio-format wav  -o '%(id)s.%(ext)s'  -i https://www.youtube.com/watch?v=fKopy74weus && sox fKopy74weus.wav -r 24000 -n remix 1 trim 25 00:00:60.00 spectrogram -Y 200 -X 64 -m -r -o fKopy74weus.png && convert -crop 128x129 fKopy74weus.png fKopy74weus_%d.png


brew install imagemagick

convert -crop 128x129 fK    opy74weus.png cropped_%d.png


time youtube-dl --extract-audio --quiet  --audio-format wav  -o '%(id)s.%(ext)s'  -i https://www.youtube.com/watch?v=PDWNJgajQ9k && sox PDWNJgajQ9k.wav -r 24000 -n remix 1 trim 25 00:00:60.00 spectrogram -Y 200 -X 64 -m -r -o PDWNJgajQ9k.png && convert -crop 128x129 PDWNJgajQ9k.png PDWNJgajQ9k_%d.png



Code
/bigdata1/homedirs/gerasoul/gpu/DeepAudioClassification/GUNJAN/UpdadtedCodeForProf


Data for Testing
/bigdata1/homedirs/gerasoul/gpu/DeepAudioClassification/GUNJAN/UpdadtedCodeForProf/Data/Slices

/bigdata1/homedirs/gerasoul/gpu/DeepAudioClassification/GUNJAN/UpdadtedCodeForProf/Data/SlicesPredict

Models for predictions
/gpu2/apo/models_for_prediction

./youtube-dl --extract-audio --quiet  --audio-format wav  -o '%(id)s.%(ext)s'  -i 'https://www.youtube.com/watch?v=fKopy74weus' && sox fKopy74weus.wav -r 24000 -n remix 1 trim 25 00:00:60.00 spectrogram -Y 200 -X 64 -m -r -o fKopy74weus.png && convert -crop 128x129 fKopy74weus.png fKopy74weus_%d.png
