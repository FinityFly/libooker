from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import requests
from datetime import datetime, timedelta
import time
import pytz
import json

class Booker:

    def __init__(self, days, start_hour, end_hour, headless=True):
        self.BASE_URL = "https://carletonu.libcal.com/spaces?lid=2986&gid=0&c=0"
        if headless:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            self.driver = webdriver.Chrome(options=chrome_options)
        else:
            self.driver = webdriver.Chrome()
        self.days = days
        self.start_hour = start_hour
        self.end_hour = end_hour

    def click_next_day(self, visited_dates):
        # check if existing booking is already selected, if there is, remove it
        try:
            button = self.driver.find_element(By.CLASS_NAME, "input-group-btn")
            button.click()
        except NoSuchElementException:
            print("Element with class 'input-group-btn' does not exist.")

        goToDateButton = self.driver.find_element(By.CLASS_NAME, "fc-goToDate-button")
        goToDateButton.click()
        table = self.driver.find_element(By.CLASS_NAME, "table-condensed")
        calendar = table.find_element(By.TAG_NAME, "tbody")
        calendar_rows = calendar.find_elements(By.TAG_NAME, "tr")

        for row in calendar_rows:
            calendar_cells = row.find_elements(By.TAG_NAME, "td")
            for cell in calendar_cells:
                timestamp = cell.get_attribute('data-date')[:-3]
                dt_object = datetime.fromtimestamp(int(timestamp), tz=pytz.UTC)
                day_of_week = dt_object.weekday()
                today_date = datetime.now().date()
                if (today_date + timedelta(days=8)) > dt_object.date() > today_date and day_of_week in self.days and dt_object.date() not in visited_dates:
                    visited_dates.append(dt_object.date())
                    print("Visiting:", dt_object.date())
                    cell.click()
                    return True
                elif dt_object.date() in visited_dates:
                    print("Skipping:", dt_object.date())
                    continue
                elif dt_object.date() > (today_date + timedelta(weeks=2)):
                    print("No more available dates, finishing...")
                    return False
        return False

    def find_available_rooms(self):
        available_rooms = []
        grid = self.driver.find_elements(By.CLASS_NAME, "fc-timeline-event-harness")
        for index, cell in enumerate(grid):
            # print(f"{index+1}/{len(grid)} - {len(available_rooms)}")
            cell = cell.find_element(By.TAG_NAME, 'a')
            title = cell.get_attribute('title').split(' ')
            date_str = ' '.join(title[:5])
            date_format = '%I:%M%p %A, %B %d, %Y'
            parsed_date = datetime.strptime(date_str, date_format)

            if title[-1] == 'Available' and self.start_hour <= parsed_date.hour < self.end_hour:
                # print("Available:", parsed_date)
                available_rooms.append({"start": parsed_date, "end": parsed_date + timedelta(minutes=30), "room": title[6], "element": cell})

        return available_rooms

    def merge_bookings(self, available_rooms):
        if not available_rooms:
            return []

        merged_bookings = []
        current_booking = available_rooms[0]

        for i in range(1, len(available_rooms)):
            next_booking = available_rooms[i]

            if current_booking['end'] == next_booking['start']:
                current_booking['end'] = next_booking['end']
            else:
                booking_time_minutes = (current_booking['end'] - current_booking['start']).total_seconds() / 60
                current_booking['booking_time'] = int(booking_time_minutes)
                merged_bookings.append(current_booking)
                current_booking = next_booking

        booking_time_minutes = (current_booking['end'] - current_booking['start']).total_seconds() / 60
        current_booking['booking_time'] = int(booking_time_minutes)
        merged_bookings.append(current_booking)

        return merged_bookings

    def book_room(self, room):
        # add room to selection
        room["element"].click()
        self.driver.implicitly_wait(5)
        time.sleep(2)

        # select latest end time
        print("1")
        select_element = self.driver.find_element(By.ID, "bookingend_1")
        select_element.click()
        print("2")
        select = Select(select_element)
        last_option = select.options[-1]
        select.select_by_visible_text(last_option.text)
        print("3")

        date_string_cleaned = last_option.text.replace('rd', '').replace('th', '').replace('st', '')
        date_format = '%I:%M%p %a %b %d %Y'
        dt_object = datetime.strptime(date_string_cleaned, date_format)
        print("4")
        room["end"] = dt_object
        self.driver.implicitly_wait(5)
        print("5")

        self.driver.find_element(By.ID, "submit_times").click()
        self.driver.implicitly_wait(5)
        print("6")

        # check if element exists
        try:
            username_input = self.driver.find_element(By.ID, "userNameInput")
            password_input = self.driver.find_element(By.ID, "passwordInput")
            with open('credentials.json', 'r') as file:
                credentials = json.load(file)
            for credential in credentials:
                username_input.send_keys(credential.get("username"))
                password_input.send_keys(credential.get("password"))
                self.driver.find_element(By.ID, "kmsiInput").click()
                self.driver.find_element(By.ID, "submitButton").click()
                self.driver.implicitly_wait(5)
                break
        except NoSuchElementException:
            print("Already logged in")
            # already logged in, just book the room
            pass

        try:
            self.driver.find_element(By.ID, "terms_accept").click()
            self.driver.implicitly_wait(5)

            self.driver.find_element(By.ID, "btn-form-submit").click()
            self.driver.implicitly_wait(5)

            self.driver.find_element(By.ID, "s-lc-eq-success-buttons").find_element(By.CLASS_NAME, "btn-primary").click()
            self.driver.implicitly_wait(5)

            self.store_booking(room)
            print(f"Successfully booked room {room['room']} on {room['start']}-{room['end']} for {room['booking_time']} minutes")
            return True
        except NoSuchElementException:
            print("Failed to finalize booking the room")
            return False

    def store_booking(self, room):
        # store booking in bookings.json
        with open('bookings.json', 'r') as file:
            bookings = json.load(file)
        bookings.append({"start": room["start"].strftime('%Y-%m-%d %H:%M:%S'), "end": room["end"].strftime('%Y-%m-%d %H:%M:%S'), "room": room["room"]})
        with open('bookings.json', 'w') as file:
            json.dump(bookings, file, indent=4)

    def run(self):
        self.driver.get(self.BASE_URL)
        self.driver.implicitly_wait(5)

        select_element = self.driver.find_element(By.ID, "gid")
        select = Select(select_element)
        select.select_by_visible_text('Conversational Floor (Floor 2 or 4)')
        self.driver.implicitly_wait(5)

        visited_dates = []

        # add dates from bookings to visited_dates to prevent double booking days
        with open('bookings.json', 'r') as file:
            bookings = json.load(file)
        for booking in bookings:
            date_format = '%Y-%m-%d %H:%M:%S'
            parsed_date = datetime.strptime(booking.get("start"), date_format)
            visited_dates.append(parsed_date.date())

        # go through the calendar and click on the next available Tuesday or Thursday within a week
        while self.click_next_day(visited_dates):
            # find available rooms between start_hour and end_hour
            available_rooms = self.find_available_rooms()

            # merge bookings that are back to back and sort them by elapsed booking time
            merged_rooms = self.merge_bookings(available_rooms)
            merged_rooms.sort(key=lambda x: x['booking_time'], reverse=True)
            merged_rooms.sort(key=lambda x: x['room'], reverse=True)

            # book the room with the longest booking time
            for room in merged_rooms:
                print(f"{room['start']} - {room['end']} ({room['booking_time']}) : {room['room']}")
                try:
                    if self.book_room(room):
                        break
                except:
                    print("Failed to book room, continuing...")
                    continue

        self.driver.quit()