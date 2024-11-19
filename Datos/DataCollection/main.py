import os
import json
import time
import requests
from datetime import datetime

def save_to_file(data, path):

  if not os.path.exists("results"):
    os.mkdir("results")
  path = os.path.join("results", path)

  if path.endswith(".json"):
    with open(path, "w") as file:
      json.dump(data, file, indent=2)
  
  elif path.endswith(".csv"):
    content = "\n".join([f"{row[0]},{row[1]}" for row in data])
    with open(path, "w") as file:
      for row in data:
        file.write(f"{row[0]},{row[1]}\n")

def request_api():
  API = "https://ofertadecursos.uniandes.edu.co/api/courses"
  response = requests.get(API)
  return response.json()

def check_changes(previous, current):
  # Revisa si hay cambios en la cantidad de inscritos
  changes = []
  previous_enrolled = {course["nrc"]: int(course["enrolled"]) for course in previous}
  current_enrolled = {course["nrc"]: int(course["enrolled"]) for course in current}

  for nrc in current_enrolled:
    if current_enrolled.get(nrc, 0) != previous_enrolled.get(nrc, 0):
      changes.append([nrc, current_enrolled.get(nrc, 0) - previous_enrolled.get(nrc, 0)])

  return changes

def main():

  courses = request_api()
  save_to_file(courses, "courses_202410.json")
  
  # Request each minute
  while True:

    try:
      time.sleep(60)
      new_courses = request_api()
      changes = check_changes(courses, new_courses)
      current_time = datetime.now().strftime("%Y-%m-%d %H.%M.%S")
      print(f"Se encontraron {len(changes)} cambios ({current_time})")
      save_to_file(changes, f"{current_time}.csv")
      courses = new_courses

    except Exception as error:
      current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      print(f"Ocurrió un error ({current_time}):", error)


if __name__ == "__main__":
  main()

