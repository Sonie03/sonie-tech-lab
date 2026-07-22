"""
Custom quotes manager widget.
Allows users to add, view, and delete their own motivational quotes.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QListWidget, QListWidgetItem, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt
from core.database import db

class QuotesWidget(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Custom Motivational Quotes", parent)
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        self.quote_input = QLineEdit()
        self.quote_input.setPlaceholderText("Enter quote here...")
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Author (optional)")
        
        form.addRow("Quote:", self.quote_input)
        form.addRow("Author:", self.author_input)
        layout.addLayout(form)
        
        add_btn = QPushButton("Add Quote")
        add_btn.clicked.connect(self.add_quote)
        layout.addWidget(add_btn)
        
        self.quote_list = QListWidget()
        layout.addWidget(self.quote_list)
        
        del_btn = QPushButton("Delete Selected")
        del_btn.clicked.connect(self.delete_quote)
        layout.addWidget(del_btn)
        
        self.load_quotes()

    def load_quotes(self):
        self.quote_list.clear()
        quotes = db.get_all_quotes()
        for q_id, text, author in quotes:
            item = QListWidgetItem(f'"{text}" - {author}')
            item.setData(Qt.ItemDataRole.UserRole, q_id)
            self.quote_list.addItem(item)

    def add_quote(self):
        text = self.quote_input.text().strip()
        author = self.author_input.text().strip() or "Me"
        if text:
            db.add_custom_quote(text, author)
            self.quote_input.clear()
            self.author_input.clear()
            self.load_quotes()

    def delete_quote(self):
        selected = self.quote_list.currentItem()
        if selected:
            q_id = selected.data(Qt.ItemDataRole.UserRole)
            db.delete_quote(q_id)
            self.load_quotes()
