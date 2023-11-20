from popgen import Project
import sys

p_obj = Project("./configuration.yaml")
p_obj.load_project()
p_obj.run_scenarios()
