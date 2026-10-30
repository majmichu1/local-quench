export function renderBooks(list, books) {
  list.innerHTML = '';
  for (const book of books) {
    const li = document.createElement('li');
    li.className = 'book';
    const title = document.createElement('span');
    title.className = 'title';
    title.textContent = book.title;
    const author = document.createElement('span');
    author.className = 'author';
    author.textContent = book.author;
    const year = document.createElement('span');
    year.className = 'year';
    year.textContent = book.year;
    li.append(title, ' by ', author, ' ', year);
    list.appendChild(li);
  }
}
