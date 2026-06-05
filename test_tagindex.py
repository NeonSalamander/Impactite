#!/usr/bin/env python3
"""Test script for the LadybugDB TagIndex implementation"""

import os
import tempfile
import shutil
from pathlib import Path

# Add src to path so we can import impactite modules
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from impactite.core import TagIndex, MarkdownParser

def test_tagindex_basic():
    """Test basic TagIndex functionality"""
    # Create a temporary directory for our test
    with tempfile.TemporaryDirectory() as temp_dir:
        notes_dir = Path(temp_dir) / "notes"
        notes_dir.mkdir()
        
        # Create a TagIndex instance
        tag_index = TagIndex(notes_dir)
        
        try:
            # Create some test markdown files
            file1 = notes_dir / "test1.md"
            file1.write_text("""---
tags: [python, tutorial]
---

# Test File 1

This is a test file about #python and #tutorial.
""")
            
            file2 = notes_dir / "test2.md"
            file2.write_text("""---
tags: [java, guide]
---

# Test File 2

This is a test file about #java and #guide.
""")
            
            file3 = notes_dir / "test3.md"
            file3.write_text("""# Test File 3

This file has #python and #guide tags.
""")
            
            # Test initial rebuild
            files = list(notes_dir.glob("*.md"))
            parser = MarkdownParser()
            tag_index.rebuild(files, parser)
            
            # Test get_tag_files
            tag_files = tag_index.get_tag_files()
            print("Tag files:", {k: [str(p) for p in v] for k, v in tag_files.items()})
            
            # Verify tags are present
            assert "python" in tag_files
            assert "tutorial" in tag_files
            assert "java" in tag_files
            assert "guide" in tag_files
            
            # Test get_tag_counts
            tag_counts = tag_index.get_tag_counts()
            print("Tag counts:", tag_counts)
            
            # Verify counts
            assert tag_counts["python"] == 2  # test1.md and test3.md
            assert tag_counts["tutorial"] == 1  # test1.md
            assert tag_counts["java"] == 1  # test2.md
            assert tag_counts["guide"] == 2  # test2.md and test3.md
            
            # Test get_tag_colors
            tag_colors = tag_index.get_tag_colors()
            print("Tag colors:", tag_colors)
            
            # Verify colors exist for all tags
            for tag in ["python", "tutorial", "java", "guide"]:
                assert tag in tag_colors
                assert tag_colors[tag].startswith("#")
                assert len(tag_colors[tag]) == 7  # #RRGGBB
            
            # Test form records
            form_file = notes_dir / "form.md"
            form_file.write_text("""---
type: form
destination: database
catalog: test
fields:
  - name: ["Name", string, 50]
  - age: ["Age", integer, 0]
---

# Test Form

This is a test form.
""")
            
            # Add form file to rebuild
            files_with_form = list(notes_dir.glob("*.md"))
            tag_index.rebuild(files_with_form, parser)
            
            # Test get_form_records
            form_records = tag_index.get_form_records()
            print("Form records:", form_records)
            
            # Should have one form record
            assert len(form_records) == 1
            assert form_records[0]["catalog"] == "test"
            assert form_records[0]["data"] == {}  # No actual form data filled in
            
            # Test favorites
            test_file = str(file1)
            assert not tag_index.is_favorite(test_file)
            
            tag_index.add_favorite(test_file)
            assert tag_index.is_favorite(test_file)
            
            tag_index.remove_favorite(test_file)
            assert not tag_index.is_favorite(test_file)
            
            tag_index.toggle_favorite(test_file)
            assert tag_index.is_favorite(test_file)
            
            # Test get_favorites
            favorites = tag_index.get_favorites()
            print("Favorites:", favorites)
            assert test_file in favorites
            
            print("All tests passed!")
            
        finally:
            tag_index.close()

if __name__ == "__main__":
    test_tagindex_basic()
