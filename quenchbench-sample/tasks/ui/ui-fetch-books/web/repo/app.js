import { renderBooks } from './render.js';

async function loadBooks() {
  const status = document.getElementById('status');
  status.textContent = 'Loading...';
  const response = fetch('books.json');
  const books = response.json();
  books.sort((a, b) => a.year - b.year);
  renderBooks(document.getElementById('book-list'), books);
  status.textContent = `Loaded ${books.length} books`;
}

loadBooks();
