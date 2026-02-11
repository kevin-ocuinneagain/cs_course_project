from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

app.config['FLASK_TITLE'] = ""

# --- IN-MEMORY DATA STRUCTURES (Students will modify this area) ---
# Phase 1: A simple Python List to store contacts
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self, items=None):
        self.head = None
        self.tail = None
        if items:
            for item in items:
                self.append(item)

    def append(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
            return
        self.tail.next = new_node
        self.tail = new_node

    def remove_by_name(self, name):
        prev = None
        curr = self.head
        while curr:
            if curr.data['name'].lower() == name.lower():
                if prev is None:
                    self.head = curr.next
                    if self.head is None:
                        self.tail = None
                else:
                    prev.next = curr.next
                    if prev.next is None:
                        self.tail = prev
                return curr.data
            prev = curr
            curr = curr.next
        return None

    def to_list(self):
        out = []
        curr = self.head
        while curr:
            out.append(curr.data)
            curr = curr.next
        return out

    def from_list(self, items):
        self.head = None
        self.tail = None
        for item in items:
            self.append(item)

contacts = LinkedList([
    {'name': 'Alice', 'email': 'alice@example.com'},
    {'name': 'Charlie', 'email': 'charlie@example.com'},
    {'name': 'Bob', 'email': 'bob@example.com'},
    {'name': 'Diana', 'email': 'diana@example.com'},
])

contacts_table = {}
undo_stack = []
redo_queue = []

def rebuild_hash_table():
    contacts_table.clear()
    for c in contacts.to_list():
        contacts_table[c['name'].lower()] = c

def snapshot_state():
    return [dict(c) for c in contacts.to_list()]

rebuild_hash_table()

# Searches for a contact by name, ignoring case.
# Returns the contact's name if found, else None.
def find_contact(name):
    if not name:
        return None
    return contacts_table.get(name.lower())


# --- ROUTES ---

@app.route('/')
def index():
    """
    Displays the main page.
    Eventually, students will pass their Linked List or Tree data here.
    """
    # Change the Flask HTML title to my name
    app.config['FLASK_TITLE'] = "Kevin O'Cuinneagain"
    return render_template('index.html',
                         contacts=contacts.to_list(),
                         title=app.config['FLASK_TITLE'],
                         can_undo=(len(undo_stack) > 0),
                         can_redo=(len(redo_queue) > 0))

@app.route('/add', methods=['POST'])
def add_contact():
    """
    Endpoint to add a new contact.
    Students will update this to insert into their Data Structure.
    """
    name = request.form.get('name')
    email = request.form.get('email')

    undo_stack.append(snapshot_state())
    redo_queue.clear()

    # Phase 1 Logic: Append to list
    contacts.append({'name': name, 'email': email})
    contacts_table[name.lower()] = {'name': name, 'email': email}

    return redirect(url_for('index'))

@app.route('/delete', methods=['POST'])
def delete_contact():
    name = request.form.get('name')
    if not name:
        return redirect(url_for('index'))

    undo_stack.append(snapshot_state())
    redo_queue.clear()

    removed = contacts.remove_by_name(name)
    if removed:
        contacts_table.pop(removed['name'].lower(), None)

    return redirect(url_for('index'))

@app.route('/undo', methods=['POST'])
def undo():
    if len(undo_stack) == 0:
        return redirect(url_for('index'))

    redo_queue.append(snapshot_state())

    previous_state = undo_stack.pop()
    contacts.from_list(previous_state)
    rebuild_hash_table()

    return redirect(url_for('index'))

@app.route('/redo', methods=['POST'])
def redo():
    if len(redo_queue) == 0:
        return redirect(url_for('index'))

    undo_stack.append(snapshot_state())

    next_state = redo_queue.pop(0)
    contacts.from_list(next_state)
    rebuild_hash_table()

    return redirect(url_for('index'))

@app.route('/search')
def search():
    app.config['FLASK_TITLE'] = "Kevin O'Cuinneagain"
    query = request.args.get('query')

    found = find_contact(query)

    if found:
        return render_template('index.html',
                             contacts=[found],
                             title=app.config['FLASK_TITLE'],
                             can_undo=(len(undo_stack) > 0),
                             can_redo=(len(redo_queue) > 0))

    return render_template('index.html',
                         contacts=[],
                         title=app.config['FLASK_TITLE'],
                         can_undo=(len(undo_stack) > 0),
                         can_redo=(len(redo_queue) > 0))

# --- DATABASE CONNECTIVITY (For later phases) ---
# Placeholders for students to fill in during Sessions 5 and 27
def get_postgres_connection():
    pass

def get_mssql_connection():
    pass

if __name__ == '__main__':
    # Run the Flask app on port 5000, accessible externally
    app.run(host='0.0.0.0', port=5000, debug=True)
