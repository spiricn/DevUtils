###############################################################################

# Dictionary containing all the remotes the projects
# we're using will be cloned from
DREPO_REMOTES = {"iwedia": "http://gerrit.iwedia.com"}

###############################################################################

# List of projects to clone
DREPO_PROJECTS = [
    # First project
    {
        "name": "libiwu",  # Name of the project
        "remote": "iwedia",  # Name of the remote. Must be present in the 'DREPO_REMOTES' variable
        "path": "libiwu",  # Project path relative to the build root
        "branch": "master",  # Project branch
    },
    # Second project
    {"name": "libdash", "remote": "iwedia", "path": "libdash", "branch": "master"},
    # Add more projects here as needed
]

###############################################################################

# List of builds. Each build defines what gets cloned from which project, or in other words which tag gets
# checked out, which commits get cherry-picked etc
DREPO_BUILDS = {
    # Map key is the build name
    "main_build": {
        # Build root directory. All the project paths are relative to this
        "root": "/home/build_root",
        # We can define a list of Gerrit change numbers to be cherry picked, per project
        # In this case we will cherry pick two changes, in the 'libiwu' project
        "cherrypicks": {  # Map of cherry picks. Each key should match one of the projects defined in 'DREPO_PROJECTS'
            "libiwu": [
                88022,
                88045,
            ]
        },
        # We can define a "pull" change per project. If this is set, DRepo will attempt to pull (merge) the commit over
        # the base (branch, tag, or final touch). If it's a non fast-forward pull the sync will fail
        "pulls": {"libdash": 88056},
        # Map of tags to be checked out. Each key should match one of the projects defined in 'DREPO_PROJECTS'
        # In this case we check out tag 'master_v1.5.0' for the 'libdash' project
        "tags": {"libdash": "master_v1.5.0"},
    }
}

# Pick a build from the list
DREPO_SELECTED_BUILD = "main_build"  # Value of this variable must match one of the keys of the 'DREPO_BUILDS' map (e.g. name of the build)

###############################################################################
