#!/usr/bin/env python3
"""CLI tool for managing your reading scrapbook."""

import argparse
import shutil
import uuid
from pathlib import Path

from PIL import Image

import db

MAX_WIDTH = 800
JPEG_QUALITY = 85


def process_photo(source_path):
    """Copy, resize, and compress a photo into local storage. Returns the new filename."""
    source = Path(source_path)
    if not source.exists():
        print(f"Error: photo not found at {source_path}")
        raise SystemExit(1)

    ext = source.suffix.lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        print(f"Error: unsupported image format '{ext}'. Use jpg, png, or webp.")
        raise SystemExit(1)

    new_filename = f"{uuid.uuid4().hex}.jpg"
    dest = db.PHOTOS_DIR / new_filename

    img = Image.open(source)
    img = img.convert("RGB")

    if img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / img.width
        new_height = int(img.height * ratio)
        img = img.resize((MAX_WIDTH, new_height), Image.LANCZOS)

    img.save(dest, "JPEG", quality=JPEG_QUALITY)
    return new_filename


def cmd_add(args):
    db.init_db()
    photo_filename = process_photo(args.photo)
    db.add_book(args.title, args.author, args.date, args.note, photo_filename)
    print(f"Added: {args.title} by {args.author}")


def cmd_remove(args):
    db.init_db()
    book = db.get_book(args.id)
    if not book:
        print(f"Error: no book with id {args.id}")
        raise SystemExit(1)

    # Delete the photo file
    if book.get("photo_filename"):
        photo_path = db.PHOTOS_DIR / book["photo_filename"]
        photo_path.unlink(missing_ok=True)

    db.delete_book(args.id)
    print(f"Removed: {book['title']} by {book['author']}")


def cmd_list(args):
    db.init_db()
    books = db.get_all_books()
    if not books:
        print("No books yet. Add one with: python bookshelf.py add --help")
        return

    print(f"{'ID':<5} {'Title':<35} {'Author':<25} {'Date':<12} {'Photo'}")
    print("-" * 110)
    for book in books:
        title = book["title"][:33] + ".." if len(book["title"]) > 35 else book["title"]
        author = book["author"][:23] + ".." if len(book["author"]) > 25 else book["author"]
        photo = book.get("photo_filename") or ""
        print(f"{book['id']:<5} {title:<35} {author:<25} {book['date_finished']:<12} {photo}")

    print(f"\n{len(books)} book(s) total")


def main():
    parser = argparse.ArgumentParser(description="My Bookshelf — personal reading scrapbook")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new book")
    add_parser.add_argument("--title", required=True, help="Book title")
    add_parser.add_argument("--author", required=True, help="Book author")
    add_parser.add_argument("--date", required=True, help="Date finished (YYYY-MM-DD)")
    add_parser.add_argument("--note", default="", help="Your personal note about the book")
    add_parser.add_argument("--photo", required=True, help="Path to your photo of the book cover")
    add_parser.set_defaults(func=cmd_add)

    remove_parser = subparsers.add_parser("remove", help="Remove a book by id")
    remove_parser.add_argument("id", type=int, help="Book id (use 'list' to see ids)")
    remove_parser.set_defaults(func=cmd_remove)

    list_parser = subparsers.add_parser("list", help="List all books")
    list_parser.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
