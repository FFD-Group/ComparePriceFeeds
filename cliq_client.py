from datetime import date
from dotenv import dotenv_values
from zoauth_client import ZOAuth2Client

class CliqClient(ZOAuth2Client):

    def __init__(self, tokens: dict, dc: str="eu") -> None:
        super().__init__(tokens, domain="cliq.zoho", dc=dc)

    def authorize_header(self, h: dict={}):
        h["Authorization"] = f"Zoho-oauthtoken {self.access_token}"
        h["Content-Type"] = "application/json"
        return h

    def postSimpleMessage(self, chat_name: str, card_text: str):
        query_url = f"/api/v2/channelsbyname/{chat_name}/message"

        data = {
            "text": card_text
        }
        response = self.query(query_url, d=data, json=True)
        return response

    def postInlineCard(self, chat_name: str, card_text: str, card_title: str, thumbnail: str, table_title: str,
                        table_headers: list, table_rows: list, buttons: list):
        query_url = f"/api/v2/channelsbyname/{chat_name}/message"
        data = {
            "text": card_text,
            "card": {
                "title": card_title,
                "theme": "modern-inline",
                "thumbnail": thumbnail,
            },
            "slides": [
                {
                    "type": "table",
                    "title": table_title,
                    "data": {
                        "headers": table_headers,
                        "rows": table_rows,
                    },
                    # "style": {
                    #     "width": {
                    #         33,
                    #         33,
                    #         33
                    #     },
                    #     "align": {
                    #         "center",
                    #         "center",
                    #         "center"
                    #     }
                    # }
                },
            ],
            "buttons": buttons
        }
        response = self.query(query_url, d=data, json=True)
        return response
