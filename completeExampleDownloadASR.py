import json
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi


def auth_process():
    credentials = None  # Declare credentials within the function
    # token.pickle stores the user's credentials from previously successful logins
    if os.path.exists('token.pickle'):
        print('Loading Credentials From File...')
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    # If there are no valid credentials available, then either refresh the token or log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print('Refreshing Access Token...')
            credentials.refresh(Request())
        else:
            print('Fetching New Tokens...')
            flow = InstalledAppFlow.from_client_secrets_file(
                'OLDclient_secrets.json',
                scopes=[
                    'https://www.googleapis.com/auth/youtube.readonly'
                ]
            )

            flow.run_local_server(port=8080, prompt='consent',
                                  authorization_prompt_message='')
            credentials = flow.credentials

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as f:
                print('Saving Credentials for Future Use...')
                pickle.dump(credentials, f)

    return credentials


# Call the authentication process and get the credentials
credentials = auth_process()

# Here starts the Data retrieval part
youtube = build('youtube', 'v3', credentials=credentials)

request = youtube.playlistItems().list(
    part="contentDetails",
    playlistId="PLpkXaq_xdxJshkb9ym9gYmviQYj6TIpfx",
    maxResults='1000'
)
response = request.execute()

# Empty list to store video ids
video_ids = []

for item in response['items']:
    video_id = item['contentDetails']['videoId']
    video_ids.append(video_id)

# Transcript file name
file_path = 'completeCaptions.txt'

# Get transcript for each video_id
for video_id in video_ids:
    print("Getting Video with ID: " + video_id)
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['fr'])

    # Open the file in append mode
    with open(file_path, 'a', encoding='utf-8') as file:
        # Iterate over the transcript list and write each text to the file
        for entry in transcript_list:
            # Check if the text doesn't contain angled brackets [ and ]
            if '[' not in entry['text'] and ']' not in entry['text']:
                file.write(entry['text'] + '\n')

print(f"Transcript has been saved to {file_path}")
