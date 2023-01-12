#!/usr/bin/python3

import gitlab
import os
import git
from git import Repo
import time
from datetime import date

token = os.environ['TOKEN']

gl = gitlab.Gitlab('https://gitlab.com', private_token=token)
groups = gl.projects.list()
group = gl.groups.get(8179038)
projects = group.projects.list(include_subgroups=True, all=True)
date_base = date.today()
date = date_base.strftime("%Y%m%d")

backup_dir = os.environ['BACKUPDIR']

for each in projects:
    project_id = each.attributes['id']
    project_name = each.attributes['name']
    project_path = f"{backup_dir}/{project_name}.tgz"
    # Create the export
    print(f"Exporting <{project_name}>")
    export = gl.projects.get(project_id).exports.create({})
    # Wait for the 'finished' status
    export.refresh()
    while export.export_status != 'finished':
        time.sleep(1)
        export.refresh()
    # Download the exported project
    with open(project_path, 'wb') as f:
        export.download(streamed=True, action=f.write)
    # Sleep for 30 sec    
    time.sleep(30)    
    # Print export successful statusls
    print(f"<{project_name}> was successfully exported!")
print("All repositories were successfully Exported.")