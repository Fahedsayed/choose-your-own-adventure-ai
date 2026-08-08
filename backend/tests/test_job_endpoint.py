import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from db.database import Base, SessionLocal, engine
from models.job import StoryJob
from routers.job import get_job_status


class JobEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=engine)

    def setUp(self):
        self.session = SessionLocal()
        self.session.query(StoryJob).delete()
        self.session.commit()

    def tearDown(self):
        self.session.close()

    def test_get_job_status_includes_theme(self):
        job = StoryJob(job_id="job-123", session_id="session-1", theme="space adventure", status="pending")
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)

        response = get_job_status(job_id="job-123", db=self.session)

        self.assertEqual(response.job_id, "job-123")
        self.assertEqual(response.theme, "space adventure")
        self.assertEqual(response.status, "pending")

    def test_get_job_status_returns_404_for_missing_job(self):
        with self.assertRaises(Exception) as context:
            get_job_status(job_id="missing", db=self.session)

        self.assertEqual(context.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
