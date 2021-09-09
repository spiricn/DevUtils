class VersionGenerator:
    """
    Version generator (lists tags and their matched names)
    """

    @staticmethod
    def generate(reportInfo):
        result = ""

        # Indication that at least one project contains a "dirty" flag, meaning it has commits
        # after a matched tag
        dirtyFlag = False

        # First matched clean tag name
        cleanTagName = None

        # Indication that at least one project contains a clean tag name, which doesn't match the others
        brokenFlag = False

        for proj in reportInfo.projects:
            result += "Repo:     " + proj.manifestProject.name + "\n"

            if proj.tagInfo:
                # Save initial tag name
                if not cleanTagName:
                    cleanTagName = proj.tagInfo.cleanMatchedTagName

                # Detect broken state if further tag names are not same
                elif cleanTagName != proj.tagInfo.cleanMatchedTagName:
                    brokenFlag = True

                # Detect dirty tag name and set the dirty flag
                if proj.tagInfo.matchedTagName and "-g" in proj.tagInfo.matchedTagName:
                    dirtyFlag = True

                if proj.tagInfo.matchedTagName:
                    result += "Tag name: " + proj.tagInfo.matchedTagName + "\n"
                if proj.tagInfo.headHash:
                    result += "Tag hash: " + proj.tagInfo.headHash + "\n\n"

        dirtyStr = "_dirty" if dirtyFlag else ""
        brokenStr = "_broken" if brokenFlag else ""

        result += "Version string: \n"
        if cleanTagName:
            result += cleanTagName.rstrip() + dirtyStr + brokenStr
        else:
            result += "No Version Found"

        return result
