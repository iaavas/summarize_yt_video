from flask import Flask, jsonify, request
import textrazor
import requests
from youtube_transcript_api import YouTubeTranscriptApi


def summarize_my_video(video_id):
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    available_languages = [trans.language_code for trans in transcript_list]

    english_dialects = [
        lang for lang in available_languages if lang.startswith('en')]

    transcript = transcript_list.find_manually_created_transcript(
        english_dialects)

    transcript_entries = transcript.fetch()

    transcript_text = ' '.join([entry['text'] for entry in transcript_entries])

    url = "https://api.meaningcloud.com/summarization-1.0"

    payload = {
        'key': '5839bdeacab27ff1c1a4035576b7c805',
        'txt': transcript_text,
        'sentences': 5
    }

    response = requests.post(url, data=payload)

    summary = response.json()['summary']

    return summary


def get_youtube_video_id(link):
    video_id = None
    if 'youtube.com' in link:
        query = link.split('?')[1]
        params = query.split('&')
        for param in params:
            key_value = param.split('=')
            if key_value[0] == 'v':
                video_id = key_value[1]
                break
    elif 'youtu.be' in link:
        video_id = link.split('/')[-1]
    return video_id


app = Flask(__name__)


@app.route('/summarize/', methods=['GET', 'POST'])
def summarize():
    youtube_link = request.args.get('link')

    video_id = get_youtube_video_id(youtube_link)
    summary = summarize_my_video(video_id)

    return jsonify({'summary': summary})


if __name__ == '__main__':
    app.run(debug=True)