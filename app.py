import youtube_transcript_api
from flask import Flask, render_template
from flask import request
import datetime
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline

app = Flask(__name__)

@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/time', methods=['GET', 'POST'])
def get_time():
    return str(datetime.datetime.now())

@app.route('/summarize', methods=['GET','POST'])
def get_url():
    video_url = request.args.get('youtube_url', '') 
    # return video_url
    if '=' in video_url:
        video_id = video_url.split("=")[1]
        transcript = get_transcript(video_id)
        summarized_transcript = get_summarized_transcript(transcript)
        return summarized_transcript
    else:
        return "Error: Invalid YouTube video URL."

def get_transcript(video_id):
    try:
        video_transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ''
        for caption in video_transcript:
            transcript += ' ' + caption['text']
        return transcript
    except youtube_transcript_api._errors.NoTranscriptFound:
        return "Error: no transcript found for video ID {}".format(video_id)
    except youtube_transcript_api._errors.VideoUnavailable:
        return "Error: video ID {} is unavailable".format(video_id)
    except:
        return "Error: an unknown error occurred while retrieving the transcript for video ID {}".format(video_id)

def get_summarized_transcript(transcript, max_length = 1024):
    #The Transformer model can only take text input size of maximum up to 1024 words
    chunks = [transcript[i: i + max_length] for i in range(0, len(transcript), max_length)]
    #using pipeline API for summarization task
    summarization = pipeline("summarization")
    summary, summarized_transcript = '', []
    for chunk in chunks:
        summary = summarization(chunk)[0]['summary_text']
        summarized_transcript.append(summary)
    return ' '.join(summarized_transcript)

if __name__ == '__main__':
    app.run(debug = True)

