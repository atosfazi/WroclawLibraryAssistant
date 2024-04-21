import json
from urllib.parse import quote
import requests


class BookAvailability:
    BASE_URL = "https://omnis-mbpwr.primo.exlibrisgroup.com/primaws/rest"

    def __init__(self, book_title, book_id):
        self.book_title = self.encode_polish_characters(book_title)
        self.book_id = book_id
        self.service_id = None

    @staticmethod
    def encode_polish_characters(text):
        return quote(text.strip(), safe='')

    def get_service_id_link(self, book_id):
        return (f"{self.BASE_URL}/pub/getPhysicalService/{book_id}?vid=48OMNIS_MBP:MBP&lang=pl"
                f"&recordOwner=48OMNIS_NETWORK&sourceRecordId={book_id}&resource_type=book"
                "&isRapido=false&lang=pl")

    def get_holding_id_url(self, service_id):
        return (f"{self.BASE_URL}/priv/ILSServices/titleServices/{self.book_id}/svcId/{service_id}"
                "?lang=pl&hideResourceSharing=false&isRapido=false&lang=pl&record-institution=48OMNIS_MBP")

    def get_final_url(self, service_id):
        return (
            f"{self.BASE_URL}/priv/ILSServices/holdings/{service_id}?record-institution=48OMNIS_MBP&lang=pl&lang=pl")

    def get_service_id(self):
        if self.book_id:
            url = self.get_service_id_link(self.book_id)
            response = requests.get(url)
            if response.status_code == 200:
                data = json.loads(response.text)
                self.service_id = data['physicalServiceId']

    def get_holding_id(self):
        if self.service_id:
            url = self.get_holding_id_url(self.service_id)
            response = requests.get(url)
            if response.status_code == 200:
                data = json.loads(response.text)
                locations = data.get("data", {}).get("itemInfo", {}).get("locations", [])
                for location in locations:
                    if location.get("library-code") == "27":
                        return location.get("hold-id"), location.get("holKey")
        return None

    def prepare_request_body(self, hold_id, hold_key):
        return {
            "filters": {
                "startPos": 1,
                "noItem": 6,
                "sublibrary": "27 - Łokietka",
                "holid": str(hold_id),
                "sublibs": "27 - Łokietka",
                "ilsRecordList": [{"institution": "48OMNIS_MBP", "recordId": str(self.book_id)}],
                "vid": "48OMNIS_MBP:MBP",
                "filterCall": False
            },
            "locations": [{
                "isValidUser": True,
                "organization": "48OMNIS_MBP",
                "libraryCode": "27",
                "availabilityStatus": "unavailable",
                "subLocation": "27 - Łokietka",
                "subLocationCode": "27",
                "mainLocation": "27 - Łokietka",
                "callNumber": "",
                "callNumberType": "#",
                "holdingURL": "OVP",
                "adaptorid": "ALMA_01",
                "ilsApiId": str(self.book_id),
                "holdId": str(hold_id),
                "holKey": hold_key,
                "matchForHoldings": []
            }]
        }

    def get_book_availability(self):
        self.get_service_id()
        if self.book_id and self.service_id:
            hold_info = self.get_holding_id()
            if hold_info:
                hold_id, hold_key = hold_info
                request_body = self.prepare_request_body(hold_id, hold_key)
                url = self.get_final_url(self.service_id)
                response = requests.post(url, json=request_body)
                if response.status_code == 200:
                    data = json.loads(response.text)
                    locations = data.get("data", {}).get("itemInfo", {}).get("locations", [])
                    for location in locations:
                        if location.get("library-code") == "27":
                            items = location.get("items", [])
                            for item in items:
                                status_name = item.get("itemstatusname")
                                if status_name:
                                    return status_name
        return 'brak informacji'
