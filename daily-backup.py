#!/usr/bin/python3

import gitlab
import git
import os
import subprocess
import time
import logging

# Enviroment Variables
token = os.environ['TOKEN']
backup_dir = os.environ['BACKUPDIR']
group_id = os.environ['GROUPID']

# Setup logging into a file
logging.basicConfig(filename=(f'{backup_dir}/errors.log'), 
                    format='%(asctime)s:%(message)s', 
                    datefmt='%m/%d/%Y', 
                    level=logging.ERROR)

separation_line = f'----------------------------------------------------'\
                  f'---------------------------------------------------'

# Gitlab Authorization
gl = gitlab.Gitlab('https://gitlab.com', private_token=token)
# Get group
group = gl.groups.get(group_id)
# List all projects within parent group, including subgroups
all_projects = group.projects.list(include_subgroups=True, all=True)
# Count projects within parent group
length = len(all_projects)
# Gitlab status history URL
gitlab_status = 'https://status.gitlab.com/pages/history/5b36dc6502d06804c08349f7'
# Git_lfs_fetch function with exceptions
def git_lfs_fetch():
            try:
                subprocess.run('git lfs fetch --all > /dev/null', check=True,
                                                                  shell=True,
                                                                  stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                print(f'ERROR: Fetching some of LFS Objects from remote repository failed!\n{separation_line}')
                logging.error(
                    f'Fetching some LFS Objects failed during {git_process}!'\
                    f'Remote project <{project_name}[{project_id}]> contains probably one or more broken LFS Files!'
                )
            else:
                print(f'Fetching LFS Objests...OK!')
                print(f'<{project_name}> was successfully fully updated!\n{separation_line}')

# Print the number of projects found in group.
print(
        f'############################################\n'
        f'{length} projects found in parent group.\n'
        f'############################################'
)

for each in all_projects:
    # Get project name
    project_name = each.attributes['name']
    # Get project id
    project_id = each.attributes['id']
    # Get project URL
    url = each.ssh_url_to_repo
    # Set project backup directory
    project_dir = f'{backup_dir}/{project_name}'
    # Get ID for each project in parent group
    project = gl.projects.get(each.id)
    # Get list of all project commits. 
    # If fails, log the error and continue with next project.
    try:
        gitlab_commits = project.commits.list()
    except gitlab.GitlabListError:
        print(f'ERROR: An unexpected HTTP error occurred durring listing <{project_name}> commits!\n'
            f'Skipping project...\n{separation_line}'
        )
        logging.error(
            f'An unexpected HTTP error occurred durring listing project <{project_name}[{project_id}]> commits!'\
            f'Project was be skipped!'
        )
        continue
    # Count project commits
    commits_length=len(gitlab_commits)  

    # If the project does exist, pull changes.
    if os.path.exists(project_dir):
        print(f'<{project_name}> already exists. Pulling changes...')
        git_process = 'PULL'
        os.chdir(project_dir)
        # Pull changes from project
        try:
            git.cmd.Git().pull()
        except git.GitCommandError as ssh_issue:
            if ssh_issue.stderr == 'ssh_exchange_identification':
                time.sleep(60)
                print(f'WARNING: SSH identification issue occurred. Gitlab.com is most likely having some performance issues. Trying again...')
                try:
                    git.cmd.Git().pull()
                except git.GitCommandError as ssh_issue:
                    if ssh_issue.stderr == 'ssh_exchange_identification':
                        logging.error(
                            f'An unexpected ssh_exchange_identification error occurred durring pulling project <{project_name}[{project_id}]>!'\
                            f'Gitlab is most likely having performance issues! Check its status history: {gitlab_status}'
                        )
                        raise Exception("Re-attempt to establish SSH connection with Gitlab.com failed!")

        else:  
            print(f'Pulling changes...OK!')     
            # Fetch LFS objects. If fails log the error and continue with the next project.
            git_lfs_fetch()
        
    # If the project doesn't exists yet and contains at least 1 commit, clone it
    elif not os.path.exists(project_dir) and commits_length > 0:
        print(f'<{project_name}> doesnt exist yet. Cloning...')
        git_process = 'CLONE'
        # Clone project. If fails log the error and continue with the next project.
        # Otherwise continue with fetching all lfs objects for the current project.
        try:
            git.Repo.clone_from(url, project_dir)
        except git.GitCommandError:
            print(f'WARNING: Cloning failed due to some broken LFS Objects on remote repository!\n{separation_line}')
            logging.error(
                f'Cloning failed due to broken LFS Objects!'\
                f'Remote project <{project_name}[{project_id}]> contains probably one or more broken LFS Files!'
            )
        else:
            print(f'Clonning...OK!')
            os.chdir(project_dir)
            git_lfs_fetch()

    # Pause for 5 sec
    time.sleep(5)

print(f'All repositories were successfully Cloned/Updated.')
