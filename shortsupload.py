import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def upload_video(file_path, title, description, category_id, privacy_status):
    # Authenticate and construct the API service
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        "client_secrets.json", SCOPES)
    credentials = flow.run_local_server(port=0)

    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

    # Upload the video
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status
        }
    }

    media = googleapiclient.http.MediaFileUpload(file_path, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = request.execute()
    print("Upload successful! Video ID:", response["id"])

if __name__ == "__main__":
    # Change these variables as needed
    video_file = "./outputs/"  # Path to your video file
    video_title = "reddit story  #shorts"
    video_description = "really cool description #shorts"
    video_category = "22"  # Category ID (e.g., "22" is for People & Blogs)
    video_privacy = "public"  # Options: "public", "unlisted", "private"

    upload_video(video_file, video_title, video_description, video_category, video_privacy)
