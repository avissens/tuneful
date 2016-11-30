import unittest
import os
import shutil
import json
try: from urllib.parse import urlparse
except ImportError: from urlparse import urlparse # Py2 compatibility
from io import StringIO

import sys; print(list(sys.modules.keys()))
# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "tuneful.config.TestingConfig"

from tuneful import app
from tuneful import models
from tuneful.utils import upload_path
from tuneful.database import Base, engine, session

class TestAPI(unittest.TestCase):
    """ Tests for the tuneful API """

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create folder for test uploads
        os.mkdir(upload_path())

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

        # Delete test upload folder
        shutil.rmtree(upload_path())

    def test_get_songs(self):
        """ Getting songs from a populated database """
        
        #Create example files & songs
        fileA = models.File(name="SongA.mp3")
        fileB = models.File(name="SongB.mp3")
        songA = models.Song(file=fileA)
        songB = models.Song(file=fileB)
        session.add_all([fileA, fileB, songA, songB])
        session.commit()
            
        response = self.client.get("/api/songs",
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(len(data), 2)

        songA = data[0]
        self.assertEqual(songA["id"], 1)
        self.assertEqual(songA["file"]["id"], 1)
        self.assertEqual(songA["file"]["name"], "SongA.mp3")
        
        songB = data[1]
        self.assertEqual(songB["id"], 2)
        self.assertEqual(songB["file"]["id"], 2)
        self.assertEqual(songB["file"]["name"], "SongB.mp3")

    def test_get_song(self):
        """ Getting a single song from a populated database """
        fileA = models.File(name = "SongA.mp3")
        songA = models.Song(file = fileA)
        fileB = models.File(name = "SongB.mp3")
        songB = models.Song(file = fileB)
        session.add_all([fileA, fileB, songA, songB])
        session.commit()

        response = self.client.get("/api/songs/{}".format(songB.id),
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["file"]["name"], "SongB.mp3")
        

    def test_post_song(self):
        #Add a new song
        data = {
            "file": {
                "name": "Example.mp3",
                }
            }

        response = self.client.post("/api/songs",
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(urlparse(response.headers.get("Location")).path,
                         "/api/songs/1")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["name"], "Example.mp3")

        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 1)

        song = songs[0]
        self.assertEqual(song.name, "Example.mp3")

"""
    def test_edit_song(self):
        #Editing an existing song
        file = models.File(name="Example.mp3")
        song = models.Song(file=file)
        session.add_all([file, song])
        session.commit()

        data = {
            "name": "Edited.mp3",
        }
        
        response = self.client.put("/api/songs/{}".format(song.id),
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")]
        )
      
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(urlparse(response.headers.get("Location")).path,
                         "/api/songs/{}".format(song.id))

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["file"]["name"], "Edited.mp3")
        
        # Assert that there is only one song in the database
        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 1)
        
        # Assert that the name was changed
        song = songs[0]
        self.assertEqual(file.name, "Edited.mp3")

    def test_delete_song(self):
        #Deleting songs from a populated database
        fileA = models.File(name = "SongA.mp3")
        songA = models.Song(file = fileA)
        fileB = models.File(name = "SongB.mp3")
        songB = models.Song(file = fileB)
        session.add_all([fileA, fileB, songA, songB])
        session.commit()

        response = self.client.delete("/api/songs/{}".format(songA.id),
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["message"], "Deleted song with id 1")

        # Assert that there is only one song in the database
        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 1)
        # Assert that the right song was deleted
        songB = data[1]
        self.assertEqual(songB["file"]["name"], "SongB.mp3")
"""