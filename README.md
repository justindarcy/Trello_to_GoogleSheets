# Trello_to_GoogleSheets
This script includes a GUI built in Tkinter that itterativly creates checkboxes based on the users Trello project boards. Once a board (or boards) are selected the program accesses the Trello API and gets a custom selection of data for cards in the selected boards. Once the data is captured for all selected boards the data is organized and cleaned in a pandas dataframe to prepare for export to a google sheet. The pygsheets library is utilized to send the data to a google sheet in the custom format.

Be sure to fill in the 4 inputs on lines 8 through 11 in the code before running.
Also be sure to corrrectly set up the google sheet correctly. See this link for details: https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html 
