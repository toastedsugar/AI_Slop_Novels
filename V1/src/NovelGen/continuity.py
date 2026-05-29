class Continuity:
    def __init__(self):
        self.chapters = {}
    
    def add_chapter(self, chapter_number, content):
        self.chapters[chapter_number] = content
    
    def get_chapter(self, chapter_number):
        return self.chapters.get(chapter_number)
    
    def get_changes(self, start_chapter, end_chapter):
        changes = []
        for chapter_number in range(start_chapter, end_chapter + 1):
            if chapter_number in self.chapters:
                content = self.chapters[chapter_number]
                changes.append((chapter_number, content))
        return changes