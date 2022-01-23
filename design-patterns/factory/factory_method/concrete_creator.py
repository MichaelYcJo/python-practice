from creator import Profile
from concrete_product import (
    PersonalSection,
    PatentSection,
    PublicationSection,
    AlbumSection,
)


class Linkedin(Profile):

    def create_profile(self):
        self.add_sections(PersonalSection())
        self.add_sections(PatentSection)
        self.add_sections(PublicationSection)


class Facebook(Profile):

    def create_profile(self):
        self.add_sections(PersonalSection())
        self.add_sections(AlbumSection())