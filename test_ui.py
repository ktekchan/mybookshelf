"""Tests to verify the scrapbook UI is correct and free of known rendering bugs."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).parent
CSS_PATH = ROOT / "static" / "css" / "style.css"
JS_PATH = ROOT / "static" / "js" / "app.js"
HTML_PATH = ROOT / "templates" / "index.html"


class TestCSSIntegrity(unittest.TestCase):
    """Validate CSS has no patterns known to cause rendering bugs."""

    @classmethod
    def setUpClass(cls):
        cls.css = CSS_PATH.read_text()

    def test_no_transform_on_book_card(self):
        """transform is incompatible with CSS columns in Safari — must not appear
        on .book-card base or hover."""
        base_block = re.search(r"\.book-card\s*\{([^}]*)\}", self.css)
        self.assertNotIn("transform", base_block.group(1),
                         ".book-card base must not use transform")
        hover_block = re.search(r"\.book-card:hover\s*\{([^}]*)\}", self.css)
        self.assertIsNotNone(hover_block, ".book-card:hover rule must exist")
        self.assertNotIn("transform", hover_block.group(1),
                         ".book-card:hover must not use transform")

    def test_no_contain_on_book_card(self):
        """contain breaks CSS columns rendering in Safari — must not be used."""
        base_block = re.search(r"\.book-card\s*\{([^}]*)\}", self.css)
        self.assertNotIn("contain", base_block.group(1),
                         ".book-card must not use contain (breaks Safari columns)")

    def test_no_pseudo_elements_on_book_card(self):
        """No ::before or ::after on .book-card (removed washi tape)."""
        self.assertNotRegex(
            self.css,
            r"\.book-card::(?:before|after)",
            ".book-card must not have ::before or ::after pseudo-elements",
        )

    def test_no_will_change_on_book_card(self):
        """will-change is unnecessary with contain and can cause issues."""
        base_block = re.search(
            r"\.book-card\s*\{([^}]*)\}", self.css
        )
        base_body = base_block.group(1)
        self.assertNotIn(
            "will-change",
            base_body,
            ".book-card should not have will-change",
        )

    def test_no_body_pseudo_elements(self):
        """body::before grain overlay was removed."""
        self.assertNotRegex(
            self.css,
            r"body::(?:before|after)",
            "body must not have ::before or ::after pseudo-elements",
        )

    def test_printed_photo_padding(self):
        """Cards should have padding for the printed-photo border look."""
        base_block = re.search(
            r"\.book-card\s*\{([^}]*)\}", self.css
        )
        base_body = base_block.group(1)
        self.assertIn("padding", base_body, ".book-card must have padding for photo border")

    def test_warm_shadow_exists(self):
        """Cards should have a warm-toned box-shadow."""
        base_block = re.search(
            r"\.book-card\s*\{([^}]*)\}", self.css
        )
        base_body = base_block.group(1)
        self.assertIn("box-shadow", base_body, ".book-card must have box-shadow")

    def test_hover_has_shadow(self):
        """Hover effect must include box-shadow."""
        hover_block = re.search(
            r"\.book-card:hover\s*\{([^}]*)\}", self.css
        )
        hover_body = hover_block.group(1)
        self.assertIn("box-shadow", hover_body, "hover must change box-shadow")

    def test_hover_only_safe_properties(self):
        """Hover must only use box-shadow and top (position-based lift).
        Never use transform or contain inside CSS columns."""
        hover_block = re.search(r"\.book-card:hover\s*\{([^}]*)\}", self.css)
        hover_body = hover_block.group(1)
        allowed = {"box-shadow", "top"}
        properties = [
            line.strip().split(":")[0].strip()
            for line in hover_body.strip().split(";")
            if line.strip() and ":" in line
        ]
        for prop in properties:
            self.assertIn(prop, allowed,
                          f"hover has disallowed property '{prop}', only {allowed} are safe")

    def test_masonry_columns_layout(self):
        """Grid must use CSS columns for masonry."""
        self.assertRegex(
            self.css,
            r"\.books-grid\s*\{[^}]*columns:",
            ".books-grid must use CSS columns for masonry layout",
        )

    def test_cream_background(self):
        """Background color must be warm cream #FAF7F2."""
        self.assertIn("#FAF7F2", self.css, "Background must be cream #FAF7F2")

    def test_header_divider(self):
        """Tagline should have a decorative border-bottom."""
        tagline_block = re.search(
            r"\.site-tagline\s*\{([^}]*)\}", self.css
        )
        self.assertIsNotNone(tagline_block, ".site-tagline rule must exist")
        self.assertIn(
            "border-bottom", tagline_block.group(1), "tagline must have border-bottom divider"
        )


class TestFlipCSS(unittest.TestCase):
    """Validate overlay-based book-flip CSS rules exist and are safe."""

    @classmethod
    def setUpClass(cls):
        cls.css = CSS_PATH.read_text()

    def test_book_overlay_rule_exists(self):
        """.book-overlay must exist with fixed positioning."""
        self.assertRegex(
            self.css,
            r"\.book-overlay\s*\{[^}]*position:\s*fixed",
            ".book-overlay must use position: fixed",
        )

    def test_overlay_card_has_perspective(self):
        """.overlay-card must exist with perspective for 3D page turn."""
        self.assertRegex(
            self.css,
            r"\.overlay-card\s*\{[^}]*perspective:",
            ".overlay-card must have perspective",
        )

    def test_page_front_has_z_index(self):
        """.page-front must exist with z-index."""
        block = re.search(r"\.page-front\s*\{([^}]*)\}", self.css)
        self.assertIsNotNone(block, ".page-front rule must exist")
        self.assertIn("z-index", block.group(1))

    def test_page_back_exists(self):
        """.page-back rule must exist."""
        block = re.search(r"\.page-back\s*\{([^}]*)\}", self.css)
        self.assertIsNotNone(block, ".page-back rule must exist")

    def test_page_fold_rule_exists(self):
        """.page-fold rule must exist."""
        block = re.search(r"\.page-fold\s*\{([^}]*)\}", self.css)
        self.assertIsNotNone(block, ".page-fold rule must exist")

    def test_flippable_cursor(self):
        """.book-card.flippable must set cursor: pointer."""
        self.assertRegex(
            self.css,
            r"\.book-card\.flippable\s*\{[^}]*cursor:\s*pointer",
            ".book-card.flippable must use cursor: pointer",
        )


class TestFlipJS(unittest.TestCase):
    """Validate JS creates overlay-based book-flip for cards with notes."""

    @classmethod
    def setUpClass(cls):
        cls.js = JS_PATH.read_text()

    def test_js_has_flippable_class(self):
        """JS must add 'flippable' class for cards with notes."""
        self.assertIn("flippable", self.js)

    def test_js_has_openBook_function(self):
        """JS must have openBook function."""
        self.assertIn("openBook", self.js)

    def test_js_has_closeBook_function(self):
        """JS must have closeBook function."""
        self.assertIn("closeBook", self.js)

    def test_js_creates_book_overlay(self):
        """JS must create book-overlay element."""
        self.assertIn("book-overlay", self.js)

    def test_js_creates_book_spread_structure(self):
        """JS must create two-panel book structure with front/back faces."""
        self.assertIn("page-front", self.js)
        self.assertIn("page-back", self.js)
        self.assertIn("front-face", self.js)
        self.assertIn("front-back", self.js)
        self.assertIn("page-fold", self.js)

    def test_js_has_animate_page_turn(self):
        """JS must have animatePageTurn using requestAnimationFrame."""
        self.assertIn("animatePageTurn", self.js)
        self.assertIn("requestAnimationFrame", self.js)


class TestJSIntegrity(unittest.TestCase):
    """Validate JS doesn't set problematic CSS properties."""

    @classmethod
    def setUpClass(cls):
        cls.js = JS_PATH.read_text()

    def test_no_rotation_in_js(self):
        """JS must not set --rotate or transform on cards."""
        self.assertNotIn(
            "--rotate",
            self.js,
            "JS must not set --rotate CSS property (incompatible with columns)",
        )

    def test_no_seeded_random(self):
        """seededRandom function should be removed."""
        self.assertNotIn(
            "seededRandom",
            self.js,
            "seededRandom function should be removed",
        )

    def test_card_creation_exists(self):
        """createCard function must exist."""
        self.assertIn("function createCard", self.js)

    def test_api_fetch(self):
        """Must fetch from /api/books."""
        self.assertIn('"/api/books"', self.js)


class TestHTMLIntegrity(unittest.TestCase):
    """Validate HTML structure."""

    @classmethod
    def setUpClass(cls):
        cls.html = HTML_PATH.read_text()

    def test_books_grid_exists(self):
        self.assertIn('id="booksGrid"', self.html)

    def test_css_linked(self):
        self.assertIn('href="/static/css/style.css"', self.html)

    def test_js_linked(self):
        self.assertIn('src="/static/js/app.js"', self.html)

    def test_lora_font_loaded(self):
        self.assertIn("Lora", self.html)

    def test_inter_font_loaded(self):
        self.assertIn("Inter", self.html)


try:
    from server import app as flask_app
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False


@unittest.skipUnless(HAS_FLASK, "Flask not installed — skipping server tests")
class TestServerIntegrity(unittest.TestCase):
    """Validate server serves the page correctly."""

    def test_page_loads(self):
        """Flask app should serve index.html at /."""
        with flask_app.test_client() as client:
            resp = client.get("/")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"booksGrid", resp.data)

    def test_css_serves(self):
        """CSS file should be served."""
        with flask_app.test_client() as client:
            resp = client.get("/static/css/style.css")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b".book-card", resp.data)

    def test_js_serves(self):
        """JS file should be served."""
        with flask_app.test_client() as client:
            resp = client.get("/static/js/app.js")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"createCard", resp.data)

    def test_api_books_endpoint(self):
        """API should return JSON array."""
        with flask_app.test_client() as client:
            resp = client.get("/api/books")
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.content_type, "application/json")


if __name__ == "__main__":
    unittest.main()
