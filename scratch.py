import re
from xbt_utils import interpolate


env = {
    "project_dir": "examples/c_projects",
}


print(interpolate(r"${project_dir}/main.c", env))

