from errbot import BotPlugin, botcmd
from errbot.utils import get_sender_username
import logging
import time
import datetime
import csv

class Entry:
  def __init__(self, title, creator):
    self.title = title
    self.creator = creator 
    self.description = "No description. :("
    self.timestamp = time.time()
    self.assignees = []

class TodoList(BotPlugin):

  ##############################################################################
  # Triggers on plugin activation,
  # loads the old todolist from a
  # file if it exists.
  ##############################################################################
  def activate(self):
    # Read the csv file if it exists and initialise the list
    self.l = []
    try:
      with open('todolist.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
          temp_entry = Entry(row[0], row[1])
          temp_entry.description = row[2]
          temp_entry.timestamp = float(row[3])
          temp_entry.assignees = [a for a in row[4::]]
          self.l.append(temp_entry)
    except IOError:
      logging.debug("Failed to load the list from the csv file. Creating a new list.")

    super(TodoList, self).activate()

  def write_csv_file(self):
    with open("todolist.csv", "w") as csv_file:
      csv_writer = csv.writer(csv_file)
      for item in self.l:
        row = [item.title, item.creator, item.description, item.timestamp] + [a for a in item.assignees]
        csv_writer.writerow([str(s) for s in row])

  @botcmd
  def todolist_list(self, mess, args):
    ret = "Listing all entries of the todolist:"
    for i, item in enumerate(self.l):
      # Add the item's id in the list and the title to the output
      ret += "\n[" + str(i) + "] " + item.title + ":\n"
      # Add the description to the output
      ret += item.description
      # Add the assignees to the output
      if len(self.l[i].assignees) > 0:
        ret += "\nAssigned to this entry: " + ", ".join(self.l[i].assignees)
      # Add the creator and a timestamp to the output
      ret += "\n(by " + item.creator + ", " + datetime.datetime.fromtimestamp(item.timestamp).strftime('%d.%m.%Y %H:%M:%S') + ")"
    return ret

  @botcmd
  def todolist_create(self, mess, args):
    self.l.append(Entry(args, get_sender_username(mess)))
    self.write_csv_file()
    return "Created a new entry with id " + str(len(self.l)-1) + ", use !todolist describe" + str(len(self.l)-1) + " to add a detailed description to it."

  @botcmd(split_args_with=' ')
  def todolist_remove(self, mess, args):
    i = int(args[0])
    if i < len(self.l):
      temp_title = self.l[i].title
      del self.l[i]
      self.write_csv_file()
      return "Successfully changed the description of entry [" + str(i) + "] " + temp_title + "."
    else:
      return "Couldn't find the todo list entry " + str(i) + ", sorry. Use !todolist list to see all entries and their indices."

  @botcmd(split_args_with=' ')
  def todolist_describe(self, mess, args):
    i = int(args[0])
    if i < len(self.l):
      self.l[i].description = ' '.join(args[1::])
      self.write_csv_file()
      return "Successfully changed the description of entry [" + str(i) + "] " + self.l[i].title + "."
    else:
      return "Couldn't find the todo list entry " + str(i) + ", sorry. Use !todolist list to see all entries and their indices."

  @botcmd(split_args_with=' ')
  def todolist_assign(self, mess, args):
    i = int(args[0])
    if i < len(self.l):
      self.l[i].assignees += args[1::]
      self.write_csv_file()
      return "Successfully assigned " + ", ".join(args[1::]) + " to [" + str(i) + "] " + self.l[i].title + "."
    else:
      return "Couldn't find the todo list entry " + str(i) + ", sorry. Use !todolist list to see all entries and their indices."

  @botcmd(split_args_with=' ')
  def todolist_unassign(self, mess, args):
    i = int(args[0])
    if i < len(self.l):
      self.l[i].assignees = [a for a in self.l[i].assignees if a not in args[1::]]
      self.write_csv_file()
      return "Successfully unassigned " + ", ".join(args[1::]) + " from [" + str(i) + "] " + self.l[i].title + "."
    else:
      return "Couldn't find the todo list entry " + str(i) + ", sorry. Use !todolist list to see all entries and their indices."
