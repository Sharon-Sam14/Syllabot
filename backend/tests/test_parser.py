from backend.parsers.syllabus_parser import SyllabusParser


def test_parser_basic_structure():
    raw_syllabus = """
    Unit 1: Introduction to Web Dev
    Chapter 1: HTML Basics
    1.1 Tags and Elements
    1.2 Attributes
    Unit 2: Advanced CSS
    Chapter 2: Flexbox Layout
    """
    
    tree = SyllabusParser.parse(raw_syllabus)
    
    # We should have 2 root nodes (Unit 1 and Unit 2)
    assert len(tree) == 2
    
    # Validate Unit 1
    u1 = tree[0]
    assert "Unit 1: Introduction to Web Dev" in u1["title"]
    assert u1["level"] == 0
    assert u1["confidence"] == 1.0
    assert len(u1["children"]) == 1  # Chapter 1
    
    # Validate Chapter 1
    ch1 = u1["children"][0]
    assert "Chapter 1: HTML Basics" in ch1["title"]
    assert ch1["level"] == 1
    assert ch1["parent_id"] == u1["id"]
    assert len(ch1["children"]) == 2  # 1.1 and 1.2
    
    # Validate 1.1 and 1.2
    t11 = ch1["children"][0]
    t12 = ch1["children"][1]
    assert t11["title"] == "1.1 Tags and Elements"
    assert t11["level"] == 2
    assert t11["parent_id"] == ch1["id"]
    
    assert t12["title"] == "1.2 Attributes"
    assert t12["level"] == 2
    assert t12["parent_id"] == ch1["id"]

    # Validate Unit 2
    u2 = tree[1]
    assert "Unit 2: Advanced CSS" in u2["title"]
    assert len(u2["children"]) == 1
    
    ch2 = u2["children"][0]
    assert "Chapter 2: Flexbox Layout" in ch2["title"]


def test_parser_bullets_and_free_text():
    raw_syllabus = """
    Unit A: Algorithms
    - Sorting Algorithms
      * Bubble Sort
      * Quick Sort
    Some free text details
    """
    
    tree = SyllabusParser.parse(raw_syllabus)
    
    assert len(tree) == 1  # Unit A is the single root node; free text is nested under Sorting Algorithms because of its level.
    
    uA = tree[0]
    assert "Unit A: Algorithms" in uA["title"]
    assert len(uA["children"]) == 1
    
    sorting = uA["children"][0]
    assert sorting["title"] == "Sorting Algorithms"
    assert sorting["confidence"] == 0.8
    
    # children of sorting: Bubble, Quick, and free text
    assert len(sorting["children"]) == 3
    assert sorting["children"][0]["title"] == "Bubble Sort"
    assert sorting["children"][0]["confidence"] == 0.8
    assert sorting["children"][1]["title"] == "Quick Sort"
    assert sorting["children"][2]["title"] == "Some free text details"
    assert sorting["children"][2]["confidence"] == 0.4
