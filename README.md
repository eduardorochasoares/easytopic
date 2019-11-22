# edVseg (Educational Video Segmenter) :man_teacher:

## Description
``edVseg`` is a versatile architecture for automatically performing topic segmentation on video lectures. 

Video lectures are very popular nowadays. Following the new teaching trends, people are increasingly seeking educational videos on the web
for the most different purposes: learn something new, review content for exams or just out of curiosity. Unfortunately, finding specific
content in this type of video is not an easy task. Many video lectures are extensive and cover several topics, and not all of these topics
are relevant to the user who has found the video. The result is that the user spends so much time trying to find topic of interest in the
middle of content irrelevant to him. The temporal segmentation of video lectures in topics can solve this problem allowing users to
navigate of a non-linear way through all topics of a video lecture. However, temporal video lecture segmentation is not an easy task
and needs to be automatized.


And that's where ``edVseg`` comes in. The architecture provides the entire processing pipeline from feature extraction to
timestamp topic detection. The use of only extracted audio features automatically makes it a versatile approach that can be employed in
a large universe of video lectures, as it does not depend on the availability of other sources such as slide shows, textbooks, 
or subtitle manually generated.

This architecture is derived from my master's thesis and you can check the [Publications section](#publications) for aditional information.

## Requirements
All you need is [Docker](https://www.docker.com/) to run `edVseg`. To install it, just follow the guide for your OS:

- [MacOS](https://docs.docker.com/docker-for-mac/install/)

* [Windows](https://docs.docker.com/docker-for-windows/install/)

- [Ubuntu](https://phoenixnap.com/kb/how-to-install-docker-on-ubuntu-18-04)

## Running dockerized version

### **⚠️This guide is valid only to Unix-based distributions. If you have Windows, some commands may be different**


First of all, we need to get some models used by our architecture. 

The first is the automatic speech recognition model trained using the [Kaldi](https://kaldi-asr.org/) toolkit.

To do this, open the `Terminal` program in your computer. Then, execute the following commands:


```sh

sudo mkdir /media/kaldi_models
cd /media/kaldi_models
wget https://phon.ioc.ee/~tanela/tedlium_nnet_ms_sp_online.tgz
tar -zxvf tedlium_nnet_ms_sp_online.tgz
```


Next, we need to download the Word2Vec model used by our segmentation algorithm. For this, follow the instructions:

```sh

sudo mkdir /media/word2vec
cd /media/word2vec

wget --save-cookies cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=0B7XkCwpI5KDYNlNUTTlSS21pQmM' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/Code: \1\n/p'
```
This will generate a `ID` as output. So, you have to type the following command:

**Make sure to replace the confirm ID with yours.**

```sh

wget --load-cookies cookies.txt 'https://docs.google.com/uc?export=download&confirm=YOURCODEID&id=0B7XkCwpI5KDYNlNUTTlSS21pQmM' -O GoogleNews-vectors-negative300.bin.gz'
```

After these steps, all you need is to extract the word2vec model:

```sh

gunzip GoogleNews-vectors-negative300.bin.gz

```

Now, you have downloaded the models required by the architecture, you need to clone or [download](https://github.com/eduardorochasoares/edVseg/master.zip) the repository.

```sh

git clone https://github.com/eduardorochasoares/edVseg

```

If you opted for the download, unzip the file and change into your downloads directory in the `Terminal`. Otherwise, just change into `edVseg's` folder:

```sh

cd edVseg

```
Lastly, to bring up the architecthure just run the command below. It launches two all containers that compose the architecture.

```sh

docker-compose up

```


## Publications
