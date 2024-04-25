'''
    This code is to update all your repos. 
'''

from git import Repo
import os

def update_repo_and_submodules(repo_path):
    """
        Update the main repository and all submodules.
    """
    print('Updating repo Main repo')
    # Pull changes for the main repository
    main_repo = Repo(repo_path)
    origin = main_repo.remotes.origin
    origin.pull()
    print(f'\t Finished update: Main repo')

    
    # Read the .gitmodules file
    gitmodules_path = os.path.join(repo_path, '.gitmodules')
    with open(gitmodules_path, 'r') as f:
        lines = f.readlines()

    # Parse the .gitmodules file to extract submodule information
    submodules = [line.split('=')[1].strip() for line in lines if line.strip().startswith('path')]

    # Pull changes for each submodule
    for submodule_path in submodules:
        print(f'Updating repo {submodule_path}...')
        submodule_path = os.path.join(repo_path, submodule_path)
        submodule_repo = Repo(submodule_path)
        origin = submodule_repo.remotes.origin
        origin.pull()
        print(f'\t Finished update: {submodule_path}')

if __name__ == '__main__':
    update_repo_and_submodules(os.getcwd())