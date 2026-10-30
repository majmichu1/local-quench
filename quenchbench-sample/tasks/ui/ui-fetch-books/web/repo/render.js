export function renderBooks(list, books) {
  list.innerHTML = '';
  for (const book of books) {
    const li = document.createElement('li');
    li.className = 'book';
    li.innerHTML = `<span class="title">${book.name}</span> by <span class="author">${book.author}</span>
      <span class="year">${book.year}</span>`;
    list.appendChild(li);
  }
}
