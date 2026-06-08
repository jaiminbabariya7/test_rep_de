"""DAG structure tests for data engineering reference project."""
import os, unittest

class TestDAGFiles(unittest.TestCase):
    DAG_DIR = os.path.join(os.path.dirname(__file__),'..','dags')
    def test_dags_directory_exists(self):
        self.assertTrue(os.path.isdir(self.DAG_DIR))
    def test_ingestion_dag_exists(self):
        self.assertTrue(os.path.exists(os.path.join(self.DAG_DIR,'ingestion_dag.py')))
    def test_dbt_run_dag_exists(self):
        self.assertTrue(os.path.exists(os.path.join(self.DAG_DIR,'dbt_run_dag.py')))
    def test_dag_files_are_python(self):
        for f in os.listdir(self.DAG_DIR):
            if not f.startswith('_'): self.assertTrue(f.endswith('.py'))

class TestDBTModels(unittest.TestCase):
    DBT_DIR = os.path.join(os.path.dirname(__file__),'..','dbt_project','models')
    def _sqls(self):
        r=[]
        for root,_,files in os.walk(self.DBT_DIR):
            r.extend(os.path.join(root,f) for f in files if f.endswith('.sql'))
        return r
    def test_models_exist(self):
        self.assertGreater(len(self._sqls()),0)
    def test_mart_uses_ref(self):
        for p in self._sqls():
            if 'mart' in p:
                self.assertIn('ref(', open(p).read(), f"{p} missing ref()")

if __name__ == "__main__": unittest.main()
