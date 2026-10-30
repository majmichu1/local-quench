import { renderBooks } from './render.js';

async function loadBooks() {
  const status = document.getElementById('status');
  const list = document.getElementById('book-list');
  status.textContent = 'Loading...';
  try {
    const response = await fetch('data/books.json');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const books = await response.json();
    if (!Array.isArray(books)) throw new Error('not a list');
    books.sort((a, b) => a.year - b.year || a.title.localeCompare(b.title));
    renderBooks(list, books);
    status.textContent = `Loaded ${books.length} ${books.length === 1 ? 'book' : 'books'}`;
  } catch (err) {
    list.innerHTML = '';
    status.textContent = 'Could not load books';
  }
}

loadBooks();
