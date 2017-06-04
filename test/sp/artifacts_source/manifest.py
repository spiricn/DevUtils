def getArtifacts():
    artifacts = []

    artifacts += [Artifact(1, 'artifacts_source/artifact1.txt', 'artifacts_dest/artifact1.txt')]
    artifacts += [Artifact(1, 'artifacts_source/artifact2.txt', 'artifacts_dest/artifact2.txt')]

    return artifacts
