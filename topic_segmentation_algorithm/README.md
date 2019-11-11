# topic_segmentation_algorithm
The implementation of an algorithm for topic segmentation in video lectures. The algorithm is based on a genetic algorithm with local search that uses some audio features from the video lecture to find the best partition of the video in topics.



Before run the program, be sure that you have all dependencies installed by running the following command.

# pip3 install -r requirements.txt

Also, please download the Google's word2vec model from https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit and extract the ".bin" to the path "topic_segmentation_algorithm/document_similarity/data/"

After that, to run the code you need to execute the following command:

# python3 summary path/of/video_lecture_features

An example of videolecture features is provided in "/example/video_lecture_features/"


# python3 summary /example/video_lecture_features/

