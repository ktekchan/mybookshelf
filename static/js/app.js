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

    if (book.note) {
      card.classList.add("flippable");
      card.addEventListener("click", () => openBook(book));
    }

    return card;
  }

  function openBook(book) {
    const overlay = document.createElement("div");
    overlay.className = "book-overlay";
    overlay.innerHTML = `
      <div class="overlay-card">
        <div class="page-recto"></div>
        <div class="page-back">
          <p class="back-title">${book.title}</p>
          <blockquote class="back-note">"${book.note}"</blockquote>
          <p class="back-hint">click to close</p>
        </div>
        <div class="page-front">
          <div class="front-face">
            <img src="/photos/${book.photo_filename}" alt="${book.title}">
            <div class="card-body">
              <h3 class="book-title">${book.title}</h3>
              <p class="book-author">by ${book.author}</p>
              <span class="book-date">${formatDate(book.date_finished)}</span>
            </div>
          </div>
          <div class="front-back"></div>
        </div>
        <div class="page-fold"></div>
      </div>
    `;
    document.body.appendChild(overlay);
    requestAnimationFrame(() => {
      overlay.classList.add("active");
      setTimeout(() => {
        const card = overlay.querySelector(".overlay-card");
        animatePageTurn(card, "open");
      }, 300);
    });
    overlay.addEventListener("click", () => closeBook(overlay));
  }

  function closeBook(overlay) {
    const card = overlay.querySelector(".overlay-card");
    animatePageTurn(card, "close", () => {
      overlay.classList.remove("active");
      setTimeout(() => {
        overlay.remove();
      }, 300);
    });
  }

  function animatePageTurn(card, direction, onComplete) {
    const front = card.querySelector(".page-front");
    const fold = card.querySelector(".page-fold");
    const duration = 800;
    const start = performance.now();

    function easeInOut(t) {
      return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }

    function tick(now) {
      const elapsed = now - start;
      const rawProgress = Math.min(elapsed / duration, 1);
      const eased = easeInOut(rawProgress);
      const progress = direction === "open" ? eased : 1 - eased;

      // Rotate front page around spine (left edge of page-front = center of card)
      const angle = progress * 180;
      front.style.transform = `rotateY(${angle}deg)`;

      // Fold shadow deepens when page is perpendicular (at 90deg)
      const foldIntensity = Math.sin(progress * Math.PI);
      fold.style.opacity = 0.3 + foldIntensity * 0.7;

      if (rawProgress < 1) {
        requestAnimationFrame(tick);
      } else {
        front.style.transform = direction === "open"
          ? "rotateY(180deg)" : "";
        fold.style.opacity = "";
        if (onComplete) onComplete();
      }
    }

    requestAnimationFrame(tick);
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
