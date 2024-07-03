import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

FLASK_API_URL = 'http://localhost:5000'

class ActionUploadFile(Action):

    def name(self) -> str:
        return "action_upload_file"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        # This action should be triggered with a file upload request
        return []

class ActionSummary(Action):

    def name(self) -> str:
        return "action_summary"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        file_path = tracker.get_slot('file_path')
        response = requests.post(f'{FLASK_API_URL}/summary', json={"file_path": file_path})
        summary = response.json()
        summary_text = '\n'.join([f"{k}: {v}" for k, v in summary.items()])
        dispatcher.utter_message(text=f"Here is the summary of the data:\n{summary_text}")
        return []

class ActionHead(Action):

    def name(self) -> str:
        return "action_head"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        file_path = tracker.get_slot('file_path')
        response = requests.post(f'{FLASK_API_URL}/head', json={"file_path": file_path})
        head = response.json()
        head_text = '\n'.join([str(row) for row in head])
        dispatcher.utter_message(text=f"Here are the first few rows of the data:\n{head_text}")
        return []

class ActionPlot(Action):

    def name(self) -> str:
        return "action_plot"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        file_path = tracker.get_slot('file_path')
        column = tracker.get_slot('column')
        response = requests.post(f'{FLASK_API_URL}/plot', json={"file_path": file_path, "column": column})
        if response.status_code == 200:
            plot_url = response.url
            dispatcher.utter_message(image=plot_url)
        else:
            dispatcher.utter_message(text="Error generating plot")
        return []
