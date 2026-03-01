document.addEventListener("DOMContentLoaded", () => {
  const grid = document.getElementById("booksGrid");
  const emptyState = document.getElementById("emptyState");

  function formatDate(dateStr) {
    const d = new Date(dateStr + "T00:00:00");
    return d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  }

  function createCard(book) {
    const card = document.createElement("div");
    card.className = "book-card";

    const noteHtml = book.note
      ? `<p class="book-note">"${book.note}"</p>`
      : "";

    card.innerHTML = `
      <img src="/photos/${book.photo_filename}" alt="${book.title}" loading="lazy">
      <div class="card-body">
        <h3 class="book-title">${book.title}</h3>
        <p class="book-author">by ${book.author}</p>
        <span class="book-date">${formatDate(book.date_finished)}</span>
        ${noteHtml}
      </div>
    `;
    return card;
  }

  fetch("/api/books")
    .then((r) => r.json())
    .then((books) => {
      if (books.length === 0) {
        emptyState.style.display = "";
        return;
      }
      emptyState.style.display = "none";
      books.forEach((book) => grid.appendChild(createCard(book)));
    })
    .catch((err) => {
      console.error("Failed to load books:", err);
    });
});
