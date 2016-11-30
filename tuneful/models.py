import os.path

from flask import url_for
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship

from tuneful import app
from .database import Base, engine

#Creating Song model - Child/Slave
class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True)
    
    #Adding ForeignKey one-2-one relationship with File
    file_id = Column(Integer, ForeignKey('files.id'), nullable=False)   
    #Using as_dictionary method
    def as_dictionary(self):
        song = {
            "id": self.id,
            "file": self.file.as_dictionary(),
            }
        return song

#Creating File model - Parent/Master
class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable = False)
    
    #Adding one-2-one relationship with Song
    song = relationship("Song", uselist=False, backref="file")
    #Using as_dictionary method
    def as_dictionary(self):
        file = {
            "id": self.id,
            "name": self.name,
        }
        return file