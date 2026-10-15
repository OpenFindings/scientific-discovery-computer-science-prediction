import unittest

from scripts.run_dbms_guidance_campaign import pair_has_databases, pair_is_complete


class GuidanceCampaignTests(unittest.TestCase):
    def test_zero_exit_without_database_is_incomplete(self):
        good = {"exit_code": 0, "databases": 1, "queries": 200,
                "successful_statements": 700, "unsuccessful_statements": 20}
        zero_database = {**good, "databases": 0, "queries": 0}
        self.assertTrue(pair_is_complete({"off": good, "on": good}, "off", "on", 1))
        self.assertFalse(pair_is_complete({"off": zero_database, "on": good}, "off", "on", 1))
        self.assertFalse(pair_has_databases({"off": zero_database, "on": good}, "off", "on", 1))

    def test_unparsed_compact_count_is_incomplete(self):
        run = {"exit_code": 0, "databases": 1, "queries": 200,
               "successful_statements": None, "unsuccessful_statements": 20}
        self.assertFalse(pair_is_complete({"off": run, "on": run}, "off", "on", 1))
        self.assertTrue(pair_has_databases({"off": run, "on": run}, "off", "on", 1))


if __name__ == "__main__":
    unittest.main()
