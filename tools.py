from llama_index.core.tools import FunctionTool, request
import os
import json
from contextvars import ContextVar
from lib import recommendation_system
yt_recommender = recommendation_system.youtube_recommender()
Notification_var: ContextVar[list] = ContextVar("Notifications", default=["",""])
Answer_var: ContextVar[list] = ContextVar("Answer", default=[])
Video_var: ContextVar[dict] = ContextVar("Videos", default={})


def recommend_videos(query):
    videos = Video_var.get()
    video_data = yt_recommender.youtube_searcher(query=query)
    videos.update(video_data)
    Video_var.set(videos)

    return "Sent Videos"

youtube_engine = FunctionTool.from_defaults(
    fn=recommend_videos,
    name="youtube",
    description="this tool is used to send youtube videos to users from search query",
)

def notification(title,body):
    Notification_var.set([title,body])
    return "Sent Notification"


notification_engine = FunctionTool.from_defaults(
    fn=notification,
    name="notification",
    description="this tool is used to send notification to user to help him",
)

def answer(message):
    message_list = Answer_var.get()
    message_list.append(message)
    Answer_var.set(message_list)
    return "Sent Message"

answer_engine = FunctionTool.from_defaults(
    fn=answer,
    name="answer",
    description="this tool is used to send reply messages to the user",
)

def storage(user_id):
    data = request.json
    filename = f"{user_id}.json"
    with open(filename, 'a') as file:
        json.dump(data, file)
        file.write('\n')
    return "Data stored successfully!"

storage_engine = FunctionTool.from_defaults(
    fn=answer,
    name="answer",
    description="this tool is used to store messages",
)

def read_data(user_id):
    filename = f"{user_id}.json"
    try:
        with open(filename, 'r') as file:
            data = file.readlines()
            return data
    except FileNotFoundError:
        return "User data not found."
    
read_engine = FunctionTool.from_defaults(
    fn=answer,
    name="answer",
    description="this tool is used to read messages",
)
    

def edit_data(user_id, new_data):
    filename = f"{user_id}.json"
    try:
        with open(filename, 'a') as file:
            json.dump(new_data, file)
            file.write('\n')
        return "Data edited successfully!"
    except FileNotFoundError:
        return "User data not found."
    
edit_engine = FunctionTool.from_defaults(
    fn=answer,
    name="answer",
    description="this tool is used to edit messages",
)