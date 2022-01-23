from abc import ABCMeta, abstractmethod


class Section(metaclass=ABCMeta):

    @abstractmethod
    def describe(self):
        pass


class PersonalSection(Section):

    def describe(self):
        print('Personal Section')


class AlbumSection(Section):

    def describe(self):
        print('Albom Section')


class PatentSection(Section):

    def describe(self):
        print('Patent Section')


class PublicationSection(Section):

    def describe(self):
        print('Publication Section')