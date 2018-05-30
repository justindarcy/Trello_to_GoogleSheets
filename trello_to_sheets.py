import requests, json, csv, re, pygsheets
from datetime import datetime
import dateutil.parser
import tkinter as tk
from itertools import zip_longest
import pandas as pd

trello_api_key = "INSERT YOUR KEY HERE"
trello_token = "INSERT TOKEN HERE"
master_list = ["INSERT LIST OF CARD NAMES HERE"]
path_to_project_key = "INSERT PATH TO GOOGLE SHEETS PROJECT KEY HERE"


# get member trello username
username = input("Enter your trello username:") 


# getting data for users board names
url = "https://api.trello.com/1/members/"+"username"+"/boards"
querystring = {"key": trello_api_key, "token": trello_token}
response_boards = requests.request("GET", url, params=querystring)

# get open_board_names and make board_keys
open_board_names = []
board_keys = {}
for board in response_boards.json():
    if board['closed'] is False:
        board_keys[board['name']] = board['id']
        open_board_names.append((board['name']))


# pasted in code from the gui module
button_dict = {}
for board in open_board_names:
    button_dict[board] = 0


def include_action_1(self):
    global chosen_boards
    chosen_boards = []
    for key, value in self.button_dict.items():
        if value.get():
            chosen_boards.append(key)
    print(chosen_boards)
    return chosen_boards


def close_window(self):
    self.root.quit()

def select_NU_action_1(self):
    global chosen_boards
    chosen_boards = []
    for key, value in self.button_dict.items():
        if "NU" in key:
            chosen_boards.append(key)
    print(chosen_boards)
    return chosen_boards


# launch gui.py to retreive the chosen_boards from gui
class GUI():
    def __init__(self, button_dict):
        self.root = tk.Tk()
        self.root.title("File Type")

        self.button_dict = button_dict
        row = len(self.button_dict) + 1

        for i, key in enumerate(self.button_dict, 1):
            self.button_dict[key] = tk.IntVar()  # set all values of the dict to intvars
            # set the variable of the checkbutton to the value of our dictionary so that our dictionary is updated each time a button is checked or unchecked
            c = tk.Checkbutton(self.root, text=key, variable=self.button_dict[key])
            c.grid(row=i, sticky=tk.W)

        include = tk.Button(self.root, text='Send Selected to Google Sheet',
                            command=self.query_include)
        include.grid(row=row, sticky=tk.W, pady=5)

        select_NU = tk.Button(self.root, text='Send All NU to Google Sheet',
                              command=self.query_select_NU)
        select_NU.grid(row=row+1, sticky=tk.W, pady=5)

        quit = tk.Button(self.root, text='Quit', command=self.root.quit)
        quit.grid(row=row+1, sticky=tk.E, padx=10, pady=5)

    def query_include(self):
        chosen_boards = include_action_1(self)
        close_window(self)
        return chosen_boards

    def query_select_NU(self):
        chosen_boards = select_NU_action_1(self)
        close_window(self)
        return chosen_boards

    def main(self):
        self.root.mainloop()


if __name__ == "__main__":
    gui = GUI(button_dict)
    gui.main()


def project_fetch(board_id):
    """
    Input: board_id, output:column1, project_output.

    This takes in a board_id and gives back the sorted and filtered trello
    board data
    """
    card_data = {}
    card_names = []

    # getting data for cards
    url_cards = "https://api.trello.com/1/boards/"+board_id+"/cards"
    querystring = {"key": trello_api_key, "token": trello_token}
    response_cards = requests.request("GET", url_cards, params=querystring)
    json_response_cards = response_cards.json()

    # getting data for lists
    url_lists = "https://api.trello.com/1/boards/"+board_id+"/lists"
    querystring = {"key": trello_api_key, "token": trello_token}
    response_lists = requests.request("GET", url_lists, params=querystring)

    # pharse board data to get matches to master_list to build card_data dict
    # card_data format is: [card_name] = [list_name, card_due_date, sort_order]
    for card_number in range(0, len(json_response_cards)):
        card_name = json_response_cards[card_number]['name']
        if any(substring in card_name for substring in master_list):
            card_names.append(card_name)
            card_data[json_response_cards[card_number]['name']] = []
            list_id = (json_response_cards[card_number]['idList'])
            for list in response_lists.json():
                if list_id == list['id']:
                    list_name = list['name']
            card_data[json_response_cards[card_number]['name']].append(list_name)

            card_due_date = (json_response_cards[card_number]['due'])

            # Convert date format if it exists and make all_card_due_dates list
            if isinstance(card_due_date, str):
                card_due_date_dt = dateutil.parser.parse(card_due_date)
                card_due_date_clean = card_due_date_dt.strftime('%b %d,%Y')
                card_due_date_clean = card_due_date_clean
            else:
                card_due_date_clean = ""

            card_data[json_response_cards[card_number]['name']].append(
                card_due_date_clean)

    # add the sort order to the card data dictionary value as item [2]
    for card_name, value in card_data.items():
        for sort_order in range(0, len(master_list)):
            if master_list[sort_order] in card_name:
                card_data[card_name].append(sort_order)

    # sort the items into the correct order with sorted_card_names
    sorted_card_names = []
    for num in range(0, len(master_list)):
        for card_name, value in card_data.items():
            if value[2] == num:
                sorted_card_names.append(card_name)

    # set up the lists that will output to the CSV
    project_output = [board_name]
    column1 = ['Deliverables'] + sorted_card_names


# loop through sorted_card_names & insert blank or output to match master_list
    for num in range(0, len(master_list)-1):
        try:
            if master_list[num+1] in sorted_card_names[num]:
                if "Progress" in card_data[sorted_card_names[num]][0]:
                    project_output.append(
                        card_data[sorted_card_names[num]][0]+", "+str(
                            card_data[sorted_card_names[num]][1]))
                elif "Complete" in card_data[sorted_card_names[num]][0]:
                    project_output.append("Complete")
                else:
                    project_output.append(str(
                        card_data[sorted_card_names[num]][1]))
            else:
                sorted_card_names[num:num] = [""]
                project_output.append("")
        except IndexError:
            sorted_card_names[num:num] = [""]
            project_output.append("")
            pass

    return project_output, column1


board_output_data = {}

# add deliverables name to the first column
status_output = master_list
status_output[0:0] = ["Deliverables"]
status_output = [status_output]


# Create empty dataframe for putput to google sheets
df_output = pd.DataFrame()
# add deliverable names to first column
df_output["Deliverables"] = master_list[1:]


# get the board id for the boards in chosen_boards and build csv output
for board_name in chosen_boards:
    board_id = board_keys[board_name]
    project_output, column1 = project_fetch(board_id)
    board_output_data[board_name] = [project_output]
    status_output.append(board_output_data[board_name][0])
    df_output[board_name] = board_output_data[board_name][0][1:]


# **send data to google sheets**
# authorization
gc = pygsheets.authorize(
    service_file=path_to_project_key) # WOrk path


# open the google spreadsheet (where 'python' is the name of the sheet)
sh = gc.open('python')

# select the first sheet
wks = sh[0]

# update the first sheet with df_output, starting at cell B2.
wks.set_dataframe(df_output, (1, 1))
