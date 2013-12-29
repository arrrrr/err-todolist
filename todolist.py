from errbot import BotPlugin, botcmd
from errbot.utils import get_sender_username
import time
import datetime

class Entry:
  def __init__(self, title, creator):
    self.title = title
    self.creator = creator 
    self.description = "No description. :("
    self.timestamp = time.time()

class TodoList(BotPlugin):

  def activate(self):
    # Triggers on plugin activation
    self.l = []
    super(TodoList, self).activate()

  @botcmd
  def todolist_list(self, mess, args):
    ret = "Listing all entries of the todolist:"
    for i, item in enumerate(self.l):
      # Add the item's id in the list and the title
      ret += "\n[" + str(i) + "] " + item.title + ":\n"
      # Add the description
      ret += item.description
      # Add the creator and a timestamp
      ret += "\n(by " + item.creator + ", " + datetime.datetime.fromtimestamp(item.timestamp).strftime('%d.%m.%Y %H:%M:%S') + ")"

    return ret

  @botcmd
  def todolist_create(self, mess, args):
    self.l.append(Entry(args, get_sender_username(mess)))
    return "Created a new entry with id " + str(len(self.l)-1) + ", use !todolist describe" + str(len(self.l)-1) + " to add a detailed description to it."

  @botcmd(split_args_with=' ')
  def todolist_describe(self, mess, args):
    i = int(args[0])
    if i < len(self.l):
      self.l[i].description = ''.join(args[1::])
      return "Successfully changed the description of entry:\n[" + str(i) + "] " + self.l[args[0]].title + "."
    else:
      return "Couldn't find the todo list entry " + str(i) + ", sorry. Use !todolist list to see all entries and their indices."
