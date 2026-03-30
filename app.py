from flask import Flask, render_template, request, redirect, url_for
import os
import heapq

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

class CategoryPathNode:
    def __init__(self, name):
        self.name = name
        self.children = {}
        self.contacts = []

class CategoryTree:
    def __init__(self):
        self.root = CategoryPathNode("root")

    def insert(self, category_path, contact):
        parts = [part.strip() for part in category_path.split("->") if part.strip()]
        curr = self.root
        curr.contacts.append(contact)

        for part in parts:
            if part not in curr.children:
                curr.children[part] = CategoryPathNode(part)
            curr = curr.children[part]
            curr.contacts.append(contact)

    def get_contacts(self, category_path):
        if not category_path:
            return self.root.contacts

        parts = [part.strip() for part in category_path.split("->") if part.strip()]
        curr = self.root

        for part in parts:
            if part not in curr.children:
                return []
            curr = curr.children[part]

        return curr.contacts

class CategoryNode:
    def __init__(self, category):
        self.category = category
        self.contacts = []
        self.left = None
        self.right = None

class CategoryBST:
    def __init__(self):
        self.root = None

    def insert(self, category, contact):
        self.root = self._insert(self.root, category.strip().lower(), contact)

    def _insert(self, node, category, contact):
        if node is None:
            node = CategoryNode(category)
            node.contacts.append(contact)
            return node

        if category < node.category:
            node.left = self._insert(node.left, category, contact)
        elif category > node.category:
            node.right = self._insert(node.right, category, contact)
        else:
            already_here = False
            for c in node.contacts:
                if c['id'] == contact['id']:
                    already_here = True
                    break
            if not already_here:
                node.contacts.append(contact)

        return node

    # REAL BST SEARCH (no traversal)
    def search(self, category):
        category = category.strip().lower()
        return self._search(self.root, category)

    def _search(self, node, category):
        if not node:
            return []

        if category < node.category:
            return self._search(node.left, category)
        elif category > node.category:
            return self._search(node.right, category)
        else:
            return node.contacts

contacts = LinkedList([
    {'id': 1, 'name': 'Alice', 'email': 'alice@example.com', 'category': 'Work -> Sales -> Team A', 'vip_priority': 3},
    {'id': 2, 'name': 'Charlie', 'email': 'charlie@example.com', 'category': 'Family -> Close', 'vip_priority': 5},
    {'id': 3, 'name': 'Bob', 'email': 'bob@example.com', 'category': 'Friends -> School', 'vip_priority': 0},
    {'id': 4, 'name': 'Diana', 'email': 'diana@example.com', 'category': 'Work -> IT -> Team B', 'vip_priority': 2},
])

next_id = 5
contacts_table = {}
category_tree = CategoryTree()
category_bst = CategoryBST()
vip_heap = []
undo_stack = []
redo_queue = []

def normalize_category(category):
    parts = [part.strip() for part in category.split("->") if part.strip()]
    return " -> ".join(parts)

def rebuild_hash_table():
    contacts_table.clear()
    for c in contacts.to_list():
        contacts_table[c['name'].lower()] = c
        contacts_table[f"id:{c['id']}"] = c

def rebuild_category_tree():
    global category_tree
    category_tree = CategoryTree()
    for c in contacts.to_list():
        category = normalize_category(c.get('category', 'Uncategorized'))
        category_tree.insert(category, c)

# FIXED BST BUILD (top-level only → actual binary tree)
def rebuild_category_bst():
    global category_bst
    category_bst = CategoryBST()
    for c in contacts.to_list():
        category = normalize_category(c.get('category', 'Uncategorized'))
        top_level = category.split("->")[0].strip()
        category_bst.insert(top_level, c)

def rebuild_vip_heap():
    global vip_heap
    vip_heap = []
    for c in contacts.to_list():
        priority = int(c.get('vip_priority', 0))
        if priority > 0:
            heapq.heappush(vip_heap, (-priority, c['id'], c))

def rebuild_structures():
    rebuild_hash_table()
    rebuild_category_tree()
    rebuild_category_bst()
    rebuild_vip_heap()

def snapshot_state():
    return [dict(c) for c in contacts.to_list()]

rebuild_structures()

def find_contact(name):
    if not name:
        return None
    for c in contacts.to_list():
        if c['name'].lower() == name.lower():
            return c
    return None

def find_contact_by_id(contact_id):
    for c in contacts.to_list():
        if c['id'] == contact_id:
            return c
    return None

def get_vip_contacts_from_heap(allowed_contacts=None):
    allowed_ids = None
    if allowed_contacts is not None:
        allowed_ids = set(c['id'] for c in allowed_contacts)

    heap_copy = list(vip_heap)
    heapq.heapify(heap_copy)

    vip_contacts = []
    seen = set()

    while heap_copy:
        priority, cid, contact = heapq.heappop(heap_copy)
        if cid in seen:
            continue
        if allowed_ids is not None and cid not in allowed_ids:
            continue
        vip_contacts.append(contact)
        seen.add(cid)

    return vip_contacts

def get_dashboard_contacts(filtered_contacts=None):
    all_contacts = filtered_contacts if filtered_contacts is not None else contacts.to_list()

    vip_contacts = get_vip_contacts_from_heap(all_contacts)
    vip_ids = set(c['id'] for c in vip_contacts)

    regular_contacts = [c for c in all_contacts if c['id'] not in vip_ids]
    regular_contacts.sort(key=lambda x: x['name'].lower())

    return vip_contacts + regular_contacts

def get_all_categories():
    categories = set()
    for c in contacts.to_list():
        category = normalize_category(c.get('category', 'Uncategorized'))
        top = category.split("->")[0].strip()
        categories.add(top)

    return sorted(categories, key=lambda x: x.lower())

# --- ROUTES ---

@app.route('/')
def index():
    app.config['FLASK_TITLE'] = "Kevin O'Cuinneagain"
    display_contacts = get_dashboard_contacts()

    return render_template(
        'index.html',
        contacts=display_contacts,
        title=app.config['FLASK_TITLE'],
        can_undo=(len(undo_stack) > 0),
        can_redo=(len(redo_queue) > 0),
        categories=get_all_categories(),
        current_filter=""
    )

@app.route('/add', methods=['POST'])
def add_contact():
    global next_id
    name = request.form.get('name')
    email = request.form.get('email')
    category = normalize_category(request.form.get('category') or 'Uncategorized')

    try:
        vip_priority = int(request.form.get('vip_priority', 0))
    except:
        vip_priority = 0

    undo_stack.append(snapshot_state())
    redo_queue.clear()

    new_contact = {
        'id': next_id,
        'name': name,
        'email': email,
        'category': category,
        'vip_priority': vip_priority
    }
    next_id += 1

    contacts.append(new_contact)
    rebuild_structures()

    return redirect(url_for('index'))

@app.route('/delete', methods=['POST'])
def delete_contact():
    name = request.form.get('name')
    if not name:
        return redirect(url_for('index'))

    undo_stack.append(snapshot_state())
    redo_queue.clear()

    contacts.remove_by_name(name)
    rebuild_structures()

    return redirect(url_for('index'))

@app.route('/filter')
def filter_contacts():
    category = normalize_category(request.args.get('category', '').strip())

    if category:
        filtered = category_bst.search(category)
    else:
        filtered = contacts.to_list()

    display_contacts = get_dashboard_contacts(filtered)

    return render_template(
        'index.html',
        contacts=display_contacts,
        title="Kevin O'Cuinneagain",
        can_undo=(len(undo_stack) > 0),
        can_redo=(len(redo_queue) > 0),
        categories=get_all_categories(),
        current_filter=category
    )

if __name__ == '__main__':
    app.run(debug=True)